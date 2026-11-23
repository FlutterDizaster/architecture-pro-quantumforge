import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

KB_DIR = Path(os.getenv("KB_DIR", ROOT / "knowledge_base"))
INDEX_DIR = Path(os.getenv("INDEX_DIR", ROOT / "index"))
LOG_DIR = Path(os.getenv("LOG_DIR", ROOT / "logs"))

EMBED_MODEL = os.getenv("EMBED_MODEL", "intfloat/multilingual-e5-small")
CHUNK_SIZE = 1600      # символов, в среднем ~175 слов английского текста
CHUNK_OVERLAP = 240    # 15%

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.anthropic.com/v1/")
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-5-5")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")

TOP_K = int(os.getenv("TOP_K", "5"))
# Ниже этого косинуса чанк считаем нерелевантным; если таких нет, в LLM не идём и отвечаем «не знаю».
MIN_SCORE = float(os.getenv("MIN_SCORE", "0.78"))
