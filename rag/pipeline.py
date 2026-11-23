"""Цепочка RAG: запрос -> эмбеддинг -> поиск в FAISS -> промпт (few-shot + CoT) -> LLM -> ответ с источниками."""
import re
from dataclasses import dataclass, field

from openai import OpenAI

from rag import config
from rag.indexing import Store
from rag.prompts import DONT_KNOW, FEW_SHOT, REFUSED, SYSTEM


@dataclass
class Answer:
    question: str
    text: str
    steps: str = ""
    sources: list[str] = field(default_factory=list)
    chunks: list[dict] = field(default_factory=list)
    found: bool = False


class RagBot:
    def __init__(self, store: Store | None = None):
        self.store = store or Store()
        self.llm = OpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)

    def retrieve(self, question: str) -> list[dict]:
        hits = self.store.search(question, config.TOP_K)
        return [h for h in hits if h["score"] >= config.MIN_SCORE]

    def build_messages(self, question: str, chunks: list[dict]) -> list[dict]:
        context = "\n\n".join(f"[{i}] {c['source']} ({c['title']}): <<<{c['text']}>>>" for i, c in enumerate(chunks, 1))
        messages = [{"role": "system", "content": SYSTEM}]
        for q, a in FEW_SHOT:
            messages += [{"role": "user", "content": q}, {"role": "assistant", "content": a}]
        messages.append({"role": "user", "content": f"КОНТЕКСТ:\n{context}\n\nВОПРОС: {question}"})
        return messages

    def ask(self, question: str) -> Answer:
        question = re.sub(r"\s+", " ", question).strip()
        chunks = self.retrieve(question)
        if not chunks:
            # пустой поиск в LLM не отдаём, иначе она начнёт отвечать по памяти
            return Answer(question, DONT_KNOW)
        resp = self.llm.chat.completions.create(
            model=config.LLM_MODEL, max_tokens=1024, messages=self.build_messages(question, chunks))
        if resp.choices[0].finish_reason == "content_filter" or not resp.choices[0].message.content:
            return Answer(question, REFUSED, chunks=chunks)
        raw = resp.choices[0].message.content or ""
        steps, _, text = raw.partition("Ответ:")
        if not text:
            steps, text = "", raw
        text = text.strip()
        used = sorted({int(n) for n in re.findall(r"\[(\d+)\]", text) if 0 < int(n) <= len(chunks)})
        sources = list(dict.fromkeys(chunks[n - 1]["source"] for n in used))
        found = bool(sources) and "не знаю" not in text.lower()
        return Answer(question, text, re.sub(r"^(Шаги|Steps):", "", steps.strip()).strip(), sources, chunks, found)
