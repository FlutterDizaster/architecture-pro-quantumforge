"""Искусственные пробелы в базе (задание 7): удаляет документ сущности и все предложения, где она упоминается."""
import re
from pathlib import Path

KB = Path(__file__).resolve().parent.parent / "knowledge_base"
ENTITIES = {
    "muirn.md": ["Muirn"],                                  # планета (в оригинале Dagobah)
    "aurite_crystal.md": ["aurite", "Aurite"],              # технология (kyber crystal)
    "teodoric_amsel_vashell.md": ["Teodor", "Teodoric", "Vashell"],  # персонаж (Lando Calrissian)
}
SENTENCE = re.compile(r"[^.!?\n]*[.!?]?")


def main() -> None:
    for doc, names in ENTITIES.items():
        (KB / doc).unlink(missing_ok=True)
        pattern = re.compile(r"\b(" + "|".join(names) + r")")
        for f in KB.glob("*.md"):
            text = f.read_text()
            if not pattern.search(text):
                continue
            kept = [line if line.startswith("#") else "".join(s for s in SENTENCE.findall(line) if not pattern.search(s))
                    for line in text.splitlines()]
            f.write_text(re.sub(r"\n{3,}", "\n\n", "\n".join(l.strip() if not l.startswith("#") else l for l in kept)) + "\n")
            print(f"{f.name}: removed mentions of {names[0]}")
        print(f"deleted {doc}")


if __name__ == "__main__":
    main()
