"""Инкрементальное обновление индекса (задание 6).

Источник: папка knowledge_base/ (в продакшне туда выгружает документы экспорт из Confluence и Git).
Новые и изменённые файлы находим по sha1 из index/manifest.json, их старые чанки удаляем по id, новые добавляем.
Чанки удалённых файлов тоже удаляются. Лог: logs/update_index.jsonl и строка в stdout.

  python update_index.py              один прогон
  python update_index.py --daily 06:00  ждать указанного времени и запускаться раз в сутки (сервис updater)
"""
import datetime as dt
import json
import sys
import time
import traceback

from rag import config
from rag.indexing import Store, file_hash

RETRIES = 3
RETRY_DELAY = 600  # секунд между повторами, если прогон упал целиком


def run() -> dict:
    started = dt.datetime.now().astimezone()
    store = Store()
    files = {f.name: f for f in sorted(config.KB_DIR.glob("*.md"))}
    added, changed, removed, new_chunks, errors = [], [], [], 0, []
    for name, path in files.items():
        old = store.manifest.get(name)
        if old == file_hash(path):
            continue
        try:
            new_chunks += store.add_file(path)  # старые чанки заменяются, только если новые посчитались
            (changed if old else added).append(name)
        except Exception as e:  # битый файл не должен ронять весь прогон, его старая версия остаётся в индексе
            errors.append(f"{name}: {e}")
    for name in [n for n in store.manifest if n not in files]:
        store.remove_file(name)
        removed.append(name)
    if added or changed or removed:
        store.save()
    finished = dt.datetime.now().astimezone()
    size = sum(p.stat().st_size for p in config.INDEX_DIR.glob("*") if p.suffix in (".index", ".json"))
    return {
        "started": started.isoformat(timespec="seconds"),
        "finished": finished.isoformat(timespec="seconds"),
        "seconds": round((finished - started).total_seconds(), 1),
        "files_added": added, "files_changed": changed, "files_removed": removed,
        "new_chunks": new_chunks, "total_chunks": store.index.ntotal, "index_bytes": size,
        "errors": errors,
    }


def log(record: dict) -> None:
    config.LOG_DIR.mkdir(exist_ok=True)
    with open(config.LOG_DIR / "update_index.jsonl", "a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    if "fatal" in record:
        print(f"index update failed at {record['started']}: {record['fatal']}", flush=True)
        return
    print(f"index updated at {record['finished'][:10]}, {len(record['files_added'])} files added, "
          f"{len(record['files_changed'])} changed, {len(record['files_removed'])} removed, "
          f"{record['new_chunks']} new chunks, {record['total_chunks']} total, "
          f"{record['index_bytes'] // 1024} KB, {len(record['errors'])} errors", flush=True)


def run_with_retries() -> bool:
    for attempt in range(1, RETRIES + 1):
        try:
            record = run()
            log(record)
            return not record["errors"]
        except Exception:
            log({"started": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "attempt": attempt,
                 "fatal": traceback.format_exc(limit=1).strip().splitlines()[-1]})
            if attempt < RETRIES:
                time.sleep(RETRY_DELAY)
    return False


def daily(at: str) -> None:
    hh, mm = map(int, at.split(":"))
    while True:
        now = dt.datetime.now()
        nxt = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if nxt <= now:
            nxt += dt.timedelta(days=1)
        print(f"next run at {nxt:%Y-%m-%d %H:%M}", flush=True)
        time.sleep((nxt - now).total_seconds())
        run_with_retries()


if __name__ == "__main__":
    if "--daily" in sys.argv:
        daily(sys.argv[sys.argv.index("--daily") + 1])
    else:
        sys.exit(0 if run_with_retries() else 1)
