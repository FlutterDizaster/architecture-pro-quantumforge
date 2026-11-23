FROM python:3.11-slim

WORKDIR /app
# torch только под CPU, иначе образ тянет CUDA на несколько гигабайт
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# модель эмбеддингов скачиваем при сборке, чтобы контейнер не качал её на каждом старте
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-small')"

COPY rag/ rag/
COPY *.py ./
CMD ["python", "telegram_bot.py"]
