"""Telegram-бот поверх RagBot. Long polling через Bot API, токен в TELEGRAM_BOT_TOKEN."""
import html
import logging
import os
import time

import httpx

from rag.pipeline import RagBot

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bot")
API = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}"
logging.getLogger("httpx").setLevel(logging.WARNING)  # иначе httpx пишет URL с токеном в лог

HELLO = ("Я отвечаю на вопросы по базе знаний QuantumForge о мире Aethari и Morrak.\n"
         "Спросите, например: «Кто обнаружил Kaelen Vossar?» или «Что такое Crimson Kestrel?»")


def render(a) -> str:
    out = html.escape(a.text)
    if a.sources:
        # имена файлов в <code>, иначе Telegram делает из "*.md" ссылки на домен .md
        out += "\n\n<i>Источники:</i> " + ", ".join(f"<code>{html.escape(s)}</code>" for s in a.sources)
    if a.steps:
        # рассуждение показываем свёрнутым, как советует курс для CoT
        out += "\n\n<blockquote expandable><b>Шаги</b>\n" + html.escape(a.steps) + "</blockquote>"
    return out


def main() -> None:
    bot = RagBot(channel="telegram")
    offset = 0
    with httpx.Client(timeout=60) as client:
        log.info("bot started")
        while True:
            try:
                updates = client.get(f"{API}/getUpdates", params={"offset": offset, "timeout": 50}).json()
            except httpx.HTTPError as e:
                log.warning("getUpdates failed: %s", type(e).__name__)
                time.sleep(5)
                continue
            for u in updates.get("result", []):
                offset = u["update_id"] + 1
                msg = u.get("message") or {}
                chat, text = msg.get("chat", {}).get("id"), (msg.get("text") or "").strip()
                if not chat or not text:
                    continue
                if text.startswith("/"):
                    client.post(f"{API}/sendMessage", json={"chat_id": chat, "text": HELLO})
                    continue
                client.post(f"{API}/sendChatAction", json={"chat_id": chat, "action": "typing"})
                try:
                    reply = render(bot.ask(text))
                except Exception:
                    log.exception("answer failed")
                    reply = "Не получилось ответить, попробуйте ещё раз позже."
                client.post(f"{API}/sendMessage", json={"chat_id": chat, "text": reply, "parse_mode": "HTML"})


if __name__ == "__main__":
    main()
