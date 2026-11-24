"""Полная сборка векторного индекса по knowledge_base/."""
import sys
import time

from rag import config
from rag.indexing import Store

SAMPLE_QUERIES = [
    "Who trained Kaelen Vossar as a Novitiate?",
    "Что уничтожило Void Core?",
    "На какой планете была база Frostpoint?",
]


def main() -> None:
    # удаляем только файлы индекса, README в папке остаётся
    for name in ("faiss.index", "chunks.json", "manifest.json"):
        (config.INDEX_DIR / name).unlink(missing_ok=True)
    t0 = time.time()
    store = Store()
    files = sorted(config.KB_DIR.glob("*.md"))
    for f in files:
        store.add_file(f)
    store.save()
    took = time.time() - t0
    words = [len(c["text"].split()) for c in store.chunks.values()]
    print(f"model: {config.EMBED_MODEL}, dim {store.index.d}")
    print(f"documents: {len(files)}, chunks: {store.index.ntotal}, words per chunk: "
          f"min {min(words)}, avg {sum(words) // len(words)}, max {max(words)}")
    print(f"built in {took:.1f} s (including model load)")
    if "--no-check" in sys.argv:
        return
    for q in SAMPLE_QUERIES:
        print(f"\nQ: {q}")
        for hit in store.search(q, 3):
            print(f"  {hit['score']:.3f} {hit['source']} #{hit['chunk_index']} [{hit['section']}] {hit['text'][:110].replace(chr(10), ' ')}...")


if __name__ == "__main__":
    main()
