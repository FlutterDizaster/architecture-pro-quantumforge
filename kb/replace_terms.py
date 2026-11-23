"""Заменяет термины вселенной на вымышленные по terms_map.json: kb/raw/ -> knowledge_base/."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "kb" / "raw"
OUT = ROOT / "knowledge_base"
TERMS = json.loads((ROOT / "terms_map.json").read_text())

# Один проход по всем ключам сразу: длинные ключи раньше коротких, замена не применяется к уже заменённому.
PATTERN = re.compile(r"(?<!\w)(" + "|".join(re.escape(k) for k in sorted(TERMS, key=len, reverse=True)) + r")(?!\w)")


def replace(text: str) -> str:
    return PATTERN.sub(lambda m: TERMS[m.group(1)], text)


def slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for src in sorted(RAW.glob("*.md")):
        text = replace(src.read_text())
        title = text.splitlines()[0].lstrip("# ").strip()
        (OUT / f"{slug(title)}.md").write_text(text)
    # Проверка: ни одного исходного термина в базе не осталось.
    leaks = {}
    for f in OUT.glob("*.md"):
        for k in TERMS:
            if re.search(r"(?<!\w)" + re.escape(k) + r"(?!\w)", f.read_text()):
                leaks.setdefault(k, []).append(f.name)
    print(f"{len(list(OUT.glob('*.md')))} documents, {len(TERMS)} terms, leaks: {len(leaks)}")
    for k, files in leaks.items():
        print(f"  {k}: {', '.join(files[:3])}")
    sys.exit(1 if leaks else 0)


if __name__ == "__main__":
    main()
