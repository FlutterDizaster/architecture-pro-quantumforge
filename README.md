# QuantumForge: RAG-бот по базе знаний

Проектная работа 7 спринта курса «Архитектор ПО». Решение в ветке `rag`, ответы по заданиям в `Project_template.md`.

## Запуск

Нужны Python 3.11 и ключ любого OpenAI-совместимого API (в пилоте Anthropic), для Telegram токен бота.

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # вписать LLM_API_KEY и TELEGRAM_BOT_TOKEN
python build_index.py       # индекс уже лежит в index/, пересборка нужна только при смене базы
python cli.py --steps       # консольный бот
python telegram_bot.py      # Telegram-бот
python update_index.py      # инкрементальное обновление индекса
```

В Docker:

```bash
docker compose up -d --build bot
docker compose run --rm indexer   # полная пересборка индекса
docker compose up -d updater      # ежедневное обновление индекса в 06:00 UTC
```

База знаний пересобирается из Wookieepedia командами
`python kb/fetch.py && python kb/replace_terms.py && python kb/remove_entities.py`
(последний скрипт вносит искусственные пробелы из задания 7), затем `python update_index.py`.

Автотест по золотому набору: `python evaluate.py` или `docker compose run --rm evaluator`.
