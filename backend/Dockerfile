FROM python:3.11-slim

# ffmpeg のインストール (動画のエンコード/結合用)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run が注入する PORT 環境変数（デフォルト8080）を受け取る設定
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
