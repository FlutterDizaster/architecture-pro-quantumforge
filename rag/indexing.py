"""Чанки, эмбеддинги и FAISS-индекс. Используется в build_index.py и update_index.py."""
import hashlib
import json
from pathlib import Path

import faiss
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from rag import config
from rag.safety import is_injection

_model = None


def model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(config.EMBED_MODEL)
    return _model


def embed_passages(texts: list[str]) -> np.ndarray:
    # e5 обучена с префиксами: "passage: " для документов, "query: " для запросов.
    vecs = model().encode([f"passage: {t}" for t in texts], batch_size=32, normalize_embeddings=True)
    return np.asarray(vecs, dtype="float32")


def embed_query(text: str) -> np.ndarray:
    vec = model().encode([f"query: {text}"], normalize_embeddings=True)
    return np.asarray(vec, dtype="float32")


splitter = RecursiveCharacterTextSplitter(
    chunk_size=config.CHUNK_SIZE,
    chunk_overlap=config.CHUNK_OVERLAP,
    separators=["\n## ", "\n### ", "\n\n", ". ", " "],
    add_start_index=True,
)


def file_hash(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()


def chunk_file(path: Path) -> list[dict]:
    text = path.read_text()
    title = text.splitlines()[0].lstrip("# ").strip()
    chunks = []
    for doc in splitter.create_documents([text]):
        body = doc.page_content.strip().lstrip(". ")
        # хвосты короче 40 слов сами по себе бесполезны, приклеиваем к предыдущему чанку
        if chunks and len(body.split()) < 40:
            chunks[-1]["text"] += " " + body
            chunks[-1]["suspicious"] = is_injection(chunks[-1]["text"])
            continue
        if len(chunks) == 1 and len(chunks[0]["text"].split()) < 10:
            # от документа остался один заголовок, склеиваем его со следующим чанком
            body = chunks.pop()["text"] + "\n\n" + body
        start = doc.metadata["start_index"]
        # ближайший заголовок раздела перед чанком, пригодится для цитирования
        heads = [line for line in text[:start + 1].splitlines() if line.startswith("##")]
        chunks.append({
            "source": path.name,
            "title": title,
            "section": heads[-1].lstrip("# ").strip() if heads else "intro",
            "chunk_index": len(chunks),
            "start": start,
            "text": body,
            "suspicious": is_injection(body),
        })
    return chunks


class Store:
    """FAISS-индекс плюс метаданные чанков в JSON рядом.

    IndexIDMap2 поверх IndexFlatIP: векторы нормализованы, поэтому скалярное произведение равно косинусу,
    а id позволяют удалять чанки изменённых файлов без полной пересборки.
    """

    def __init__(self, index_dir: Path = config.INDEX_DIR):
        self.dir = index_dir
        self.index_path = index_dir / "faiss.index"
        self.meta_path = index_dir / "chunks.json"
        self.manifest_path = index_dir / "manifest.json"
        self.loaded_at = 0.0
        if self.index_path.exists():
            self.loaded_at = self.index_path.stat().st_mtime
            self.index = faiss.read_index(str(self.index_path))
            self.chunks = {int(k): v for k, v in json.loads(self.meta_path.read_text()).items()}
            self.manifest = json.loads(self.manifest_path.read_text())
        else:
            dim = model().get_embedding_dimension()
            self.index = faiss.IndexIDMap2(faiss.IndexFlatIP(dim))
            self.chunks, self.manifest = {}, {}

    def add_file(self, path: Path) -> int:
        """Добавляет документ, а если он уже был в индексе, заменяет его чанки.

        Чанки и эмбеддинги считаются до удаления старых: если упадёт на них, старая версия документа останется в индексе.
        """
        chunks = chunk_file(path)
        vecs = embed_passages([f"{c['title']}. {c['text']}" for c in chunks]) if chunks else None
        self.remove_file(path.name)
        if not chunks:
            return 0
        start_id = max(self.chunks, default=-1) + 1
        ids = np.arange(start_id, start_id + len(chunks), dtype="int64")
        self.index.add_with_ids(vecs, ids)
        for i, c in zip(ids, chunks):
            self.chunks[int(i)] = c
        self.manifest[path.name] = file_hash(path)
        return len(chunks)

    def remove_file(self, name: str) -> int:
        ids = [i for i, c in self.chunks.items() if c["source"] == name]
        if ids:
            self.index.remove_ids(np.array(ids, dtype="int64"))
        for i in ids:
            del self.chunks[i]
        self.manifest.pop(name, None)
        return len(ids)

    def search(self, query: str, k: int = config.TOP_K) -> list[dict]:
        if self.index.ntotal == 0:
            return []
        scores, ids = self.index.search(embed_query(query), k)
        # id без метаданных (индекс и chunks.json разошлись) пропускаем, а не падаем
        return [{**self.chunks[int(i)], "id": int(i), "score": float(s)}
                for s, i in zip(scores[0], ids[0]) if int(i) in self.chunks and self.chunks[int(i)].get("text")]

    def changed_on_disk(self) -> bool:
        return self.index_path.exists() and self.index_path.stat().st_mtime > self.loaded_at

    def save(self) -> None:
        # индекс пишем последним: бот перечитывает всё по изменению faiss.index,
        # к этому моменту метаданные уже на месте
        self.dir.mkdir(parents=True, exist_ok=True)
        self.meta_path.write_text(json.dumps(self.chunks, ensure_ascii=False, indent=0))
        self.manifest_path.write_text(json.dumps(self.manifest, indent=1, sort_keys=True))
        tmp = self.index_path.with_suffix(".tmp")
        faiss.write_index(self.index, str(tmp))
        tmp.replace(self.index_path)
        self.loaded_at = self.index_path.stat().st_mtime
