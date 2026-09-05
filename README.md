# YouTube Video Downloader

FastAPI (Python) と yt-dlp を使用した、最高画質のYouTube動画ダウンロードAPIおよび軽量フロントエンドアプリケーションです。

## 概要

- **完全ステートレス**: サーバー上に動画やデータベースを保持せず、ダウンロード完了後に一時ファイルを自動削除します。
- **高画質・高音質**: `yt-dlp` と `ffmpeg` を活用し、1080p 以上の映像と音声を自動で結合して出力します。
- **モダンなUI**: Tailwind CSS を使用したシンプルかつレスポンシブなデザイン。

## 技術スタック

- **Backend**: Python 3.11+, FastAPI, yt-dlp, uvicorn, ffmpeg
- **Frontend**: HTML5, JavaScript (Fetch API), Tailwind CSS
- **Container**: Docker

## ローカルでの実行方法

### Docker を使用する場合（推奨）

```bash
# Dockerイメージのビルド
docker build -t yt-downloader .

# コンテナの起動
docker run -d -p 8000:8000 --name yt-app yt-downloader
```

起動後、ブラウザで http://localhost:8000 にアクセスしてください。

### ローカルのPython環境で実行する場合
事前に ffmpeg がシステムにインストールされている必要があります。
```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# サーバー起動
uvicorn main:app --reload --port 8000
```

## ディレクトリ構成
```
.
├── main.py            # FastAPI バックエンド処理
├── index.html         # フロントエンド画面
├── Dockerfile         # Dockerビルド設定
├── requirements.txt   # Python依存ライブラリ
├── .gitignore         # Git管理除外設定
└── README.md          # 本ファイル
```

## 免責事項 (Disclaimer)
本ツールは技術検証および個人学習を目的として作成されています。

YouTubeの利用規約に従ってご利用ください。

違法にアップロードされたコンテンツのダウンロードや、著作権を侵害する行為には使用しないでください。

本ツールの利用によって生じた一切の損害について、制作者は責任を負いません。


---
