FROM python:3.11-slim

# ffmpeg のインストール (動画のエンコード/結合用)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# FastAPI 起動設定 (ポート8000)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
