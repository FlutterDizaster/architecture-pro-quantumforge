"""Журнал запросов к боту (задание 7): logs/queries.jsonl, одна строка на запрос."""
import datetime as dt
import json

from rag import config


def log_query(answer, channel: str, latency: float, error: str = "") -> None:
    config.LOG_DIR.mkdir(exist_ok=True)
    record = {
        "ts": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "channel": channel,
        "query": answer.question,
        "chunks_found": bool(answer.chunks),
        "top_score": round(max((c["score"] for c in answer.chunks), default=0.0), 3),
        "retrieved": [c["source"] for c in answer.chunks],
        "sources": answer.sources,
        "answer": answer.text,
        "answer_len": len(answer.text),
        "success": answer.found,
        "blocked": answer.blocked,
        "filtered_chunks": answer.filtered,
        "error": error,
        "filtered_chunks": answer.filtered,
        "latency_s": round(latency, 2),
    }
    with open(config.LOG_DIR / "queries.jsonl", "a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
