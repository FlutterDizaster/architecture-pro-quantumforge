"""Консольный бот: python cli.py, пустая строка или Ctrl+D для выхода. --steps показывает рассуждение."""
import sys

from rag.pipeline import RagBot


def main() -> None:
    bot = RagBot()
    show_steps = "--steps" in sys.argv
    while True:
        try:
            q = input("\nВопрос> ").strip()
        except EOFError:
            break
        if not q:
            break
        a = bot.ask(q)
        if show_steps and a.steps:
            print(f"Шаги:\n{a.steps}")
        print(f"Ответ: {a.text}")
        if a.sources:
            print("Источники: " + ", ".join(a.sources))


if __name__ == "__main__":
    main()
