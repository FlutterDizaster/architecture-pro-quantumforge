"""Скачивает статьи Wookieepedia через MediaWiki API и сохраняет чистый текст в kb/raw/."""
import json
import re
import sys
import time
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

API = "https://starwars.fandom.com/api.php"
PAGES = Path(__file__).with_name("pages.txt")
OUT = Path(__file__).with_name("raw")
MAX_WORDS = 1100
# Разделы, после которых в статье идут источники, списки появлений и закулисье.
STOP = {"Behind the scenes", "Appearances", "Sources", "Notes and references", "External links",
        "Non-canon appearances", "Explore all of Wookieepedia", "Legends"}


def clean(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.select("table, .infobox, aside, .reference, sup, .mw-editsection, .thumb, figure, "
                           "style, script, .quote, .notice, .hatnote, .toc, .navbox, .portable-infobox"):
        tag.decompose()
    parts, words = [], 0
    for el in soup.select(".mw-parser-output > h2, .mw-parser-output > h3, .mw-parser-output > p"):
        text = re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip()
        text = re.sub(r"\s+([.,;:!?)])", r"\1", text).replace("( ", "(")
        text = re.sub(r"\s+'s\b", "'s", text)
        text = re.sub(r"(\w) -(\w)", r"\1-\2", text)
        if el.name in ("h2", "h3"):
            if text in STOP:
                break
            parts.append(("#" if el.name == "h2" else "##") + "# " + text)
            continue
        if len(text) < 40:
            continue
        parts.append(text)
        words += len(text.split())
        if words >= MAX_WORDS:
            break
    while parts and parts[-1].startswith("#"):
        parts.pop()
    return "\n\n".join(parts)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    # можно передать заголовки аргументами, чтобы докачать отдельные статьи
    titles = sys.argv[1:] or [t.strip() for t in PAGES.read_text().splitlines() if t.strip() and not t.startswith("#")]
    with httpx.Client(headers={"User-Agent": "study-project (rag course)"}, timeout=30) as client:
        for title in titles:
            r = client.get(API, params={"action": "parse", "page": title, "prop": "text", "format": "json",
                                        "redirects": 1, "disableeditsection": 1})
            data = r.json()
            if "error" in data:
                print("skip", title, data["error"].get("info"), file=sys.stderr)
                continue
            body = clean(data["parse"]["text"]["*"])
            name = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
            (OUT / f"{name}.md").write_text(f"# {data['parse']['title']}\n\n{body}\n")
            print(f"{name}: {len(body.split())} words")
            time.sleep(0.5)


if __name__ == "__main__":
    main()
