"""Автотест качества по золотому набору (задание 7).

Задаёт вопросы из golden_questions.txt, каждый запрос попадает в logs/queries.jsonl (channel=eval),
результаты по вопросам в logs/evaluation.jsonl, сводка в docs/evaluation_report.md.
Код возврата 1, если точность ниже порога: так прогон можно ставить в CI после обновления индекса.
"""
import collections
import datetime as dt
import json
import sys
from pathlib import Path

from rag import config
from rag.pipeline import RagBot

GOLDEN = Path(__file__).with_name("golden_questions.txt")
REPORT = Path(__file__).with_name("docs") / "evaluation_report.md"
MIN_ACCURACY = 0.8


def load() -> list[dict]:
    items = []
    for line in GOLDEN.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        kind, q, expected, kws, src = [p.strip() for p in line.split("|")]
        items.append({"kind": kind, "question": q, "expected": expected,
                      "keywords": [k.strip() for k in kws.split(";") if k.strip()], "source": src})
    return items


def check(item: dict, bot: RagBot) -> dict:
    try:
        a = bot.ask(item["question"])
    except Exception as e:  # сбой генерации или поиска тоже результат, а не падение прогона
        return {**item, "status": "error", "error": str(e), "correct": False}
    retrieved = [c["source"] for c in a.chunks]
    res = {**item, "answer": a.text, "answered": a.found, "retrieved": retrieved, "cited": a.sources,
           "top_score": round(max((c["score"] for c in a.chunks), default=0.0), 3)}
    if item["kind"] == "known":
        hits = [k for k in item["keywords"] if k.lower() in a.text.lower()]
        res["retrieval_hit"] = item["source"] in retrieved
        res["completeness"] = round(len(hits) / len(item["keywords"]), 2)
        res["correct"] = a.found and res["completeness"] == 1.0
    elif item["kind"] == "side":
        # тема в базе есть, а факт удалён: верно, если бот его не выдумал
        res["correct"] = not any(k.lower() in a.text.lower() for k in item["keywords"])
    else:
        res["correct"] = not a.found
    res["status"] = "ok" if res["correct"] else "fail"
    return res


def query_log_stats() -> list[str]:
    path = config.LOG_DIR / "queries.jsonl"
    if not path.exists():
        return []
    rows = [json.loads(l) for l in path.read_text().splitlines()]
    by_channel = collections.Counter(r["channel"] for r in rows)
    failed = [r for r in rows if not r["success"]]
    topics = collections.Counter(r["retrieved"][0] for r in failed if r["retrieved"])
    out = [f"Всего запросов в журнале: {len(rows)} ({', '.join(f'{k}: {v}' for k, v in by_channel.items())}), "
           f"без ответа: {len(failed)}, из них отклонено защитой: {sum(1 for r in failed if r['blocked'])}, "
           f"поиск ничего не нашёл: {sum(1 for r in failed if not r['chunks_found'])}; "
           f"запросов, где из выдачи отброшен подозрительный чанк: {sum(1 for r in rows if r.get('filtered_chunks'))}.", ""]
    if topics:
        out += ["Документы, которые чаще всего оказываются первыми в выдаче у запросов без ответа:", ""]
        out += [f"- `{doc}`: {n}" for doc, n in topics.most_common(5)]
    return out


def main() -> None:
    bot = RagBot(channel="eval")
    results = [check(i, bot) for i in load()]
    config.LOG_DIR.mkdir(exist_ok=True)
    run_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    with open(config.LOG_DIR / "evaluation.jsonl", "a") as f:
        for r in results:
            f.write(json.dumps({"run": run_at, **r}, ensure_ascii=False) + "\n")

    known = [r for r in results if r["kind"] == "known"]
    neg = [r for r in results if r["kind"] in ("removed", "absent")]
    side = [r for r in results if r["kind"] == "side"]
    acc = sum(r["correct"] for r in results) / len(results)
    lines = [
        "# Отчёт автотеста по золотому набору", "",
        f"Прогон {run_at}, модель `{config.LLM_MODEL}`, эмбеддинги `{config.EMBED_MODEL}`, "
        f"чанков в индексе {bot.store.index.ntotal}.", "",
        f"- Общая точность: {sum(r['correct'] for r in results)}/{len(results)} ({acc:.0%}).",
        f"- Известные темы: ответил верно {sum(r['correct'] for r in known)}/{len(known)}, "
        f"нужный документ в топ-{config.TOP_K} (hit@{config.TOP_K}): {sum(r.get('retrieval_hit', False) for r in known)}/{len(known)}, "
        f"средняя полнота по ключевым словам {sum(r.get('completeness', 0) for r in known) / len(known):.2f}.",
        f"- Удалённые и отсутствующие темы: корректный отказ {sum(r['correct'] for r in neg)}/{len(neg)}.",
        f"- Побочные пробелы (факт ушёл вместе с удалённой сущностью): не выдумал {sum(r['correct'] for r in side)}/{len(side)}.",
        f"- Ошибок выполнения: {sum(r['status'] == 'error' for r in results)}.", "",
        "| Тип | Вопрос | Итог | Найдено в индексе (score) | Процитировано | Ответ |", "|---|---|---|---|---|---|",
    ]
    for r in results:
        found = ", ".join(dict.fromkeys(r.get("retrieved", []))) or "—"
        lines.append(f"| {r['kind']} | {r['question']} | {r['status']} | {found} ({r.get('top_score', 0)}) | "
                     f"{', '.join(r.get('cited', [])) or '—'} | {r.get('answer', r.get('error', '')).replace(chr(10), ' ')[:160]} |")
    lines += ["", "## Журнал запросов", ""] + query_log_stats()
    REPORT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:8]))
    sys.exit(0 if acc >= MIN_ACCURACY else 1)


if __name__ == "__main__":
    main()
