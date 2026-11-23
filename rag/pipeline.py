"""Цепочка RAG: запрос -> эмбеддинг -> поиск в FAISS -> промпт (few-shot + CoT) -> LLM -> ответ с источниками."""
import re
from dataclasses import dataclass, field

from openai import OpenAI

from rag import config, safety
from rag.indexing import Store
from rag.prompts import BLOCKED_INPUT, BLOCKED_OUTPUT, DONT_KNOW, FEW_SHOT, REFUSED, SYSTEM


@dataclass
class Answer:
    question: str
    text: str
    steps: str = ""
    sources: list[str] = field(default_factory=list)
    chunks: list[dict] = field(default_factory=list)
    found: bool = False
    blocked: str = ""  # какой слой защиты отклонил запрос: input, corpus, output
    filtered: int = 0  # сколько найденных чанков отброшено как подозрительные


class RagBot:
    def __init__(self, store: Store | None = None, protection: set[str] = config.PROTECTION):
        self.store = store or Store()
        self.protection = set(protection)
        self.llm = OpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)

    def retrieve(self, question: str) -> tuple[list[dict], int]:
        """Чанки выше порога и сколько из них отброшено как подозрительные."""
        if self.store.changed_on_disk():  # индекс обновил update_index.py
            self.store = Store(self.store.dir)
        hits = [h for h in self.store.search(question, config.TOP_K) if h["score"] >= config.MIN_SCORE]
        if "corpus" not in self.protection:
            return hits, 0
        clean = [{**h, "text": safety.strip_injection(h["text"])} for h in hits if not h.get("suspicious")]
        return clean, len(hits) - len(clean)

    def build_messages(self, question: str, chunks: list[dict]) -> list[dict]:
        context = "\n\n".join(f"[{i}] {c['source']} ({c['title']}): <<<{c['text']}>>>" for i, c in enumerate(chunks, 1))
        system = SYSTEM + (safety.GUARD_RULES if "prompt" in self.protection else "")
        messages = [{"role": "system", "content": system}]
        for q, a in FEW_SHOT:
            messages += [{"role": "user", "content": q}, {"role": "assistant", "content": a}]
        messages.append({"role": "user", "content": f"КОНТЕКСТ:\n{context}\n\nВОПРОС: {question}"})
        return messages

    def ask(self, question: str) -> Answer:
        question = re.sub(r"\s+", " ", question).strip()
        if "input" in self.protection and safety.is_injection(question):
            return Answer(question, BLOCKED_INPUT, blocked="input")
        chunks, dropped = self.retrieve(question)
        if not chunks:
            # пустой поиск в LLM не отдаём, иначе она начнёт отвечать по памяти
            return Answer(question, DONT_KNOW, blocked="corpus" if dropped else "", filtered=dropped)
        resp = self.llm.chat.completions.create(
            model=config.LLM_MODEL, max_tokens=1024, messages=self.build_messages(question, chunks))
        if resp.choices[0].finish_reason == "content_filter" or not resp.choices[0].message.content:
            return Answer(question, REFUSED, chunks=chunks, filtered=dropped)
        raw = resp.choices[0].message.content
        # модель иногда пишет «Answer:» вместо «Ответ:», особенно на английские вопросы
        parts = re.split(r"(?:Ответ|Answer):", raw, maxsplit=1)
        steps, text = (parts[0], parts[1]) if len(parts) == 2 else ("", raw)
        text = text.strip()
        steps = re.sub(r"^(Шаги|Steps):", "", steps.strip()).strip()
        if "output" in self.protection and (safety.has_secret(text) or safety.has_secret(steps)):
            return Answer(question, BLOCKED_OUTPUT, chunks=chunks, blocked="output", filtered=dropped)
        used = sorted({int(n) for n in re.findall(r"\[(\d+)\]", text) if 0 < int(n) <= len(chunks)})
        sources = list(dict.fromkeys(chunks[n - 1]["source"] for n in used))
        found = bool(sources) and "не знаю" not in text.lower()
        return Answer(question, text, steps, sources, chunks, found, filtered=dropped)
