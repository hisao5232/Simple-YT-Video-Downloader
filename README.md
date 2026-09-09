# YouTube Video Downloader

FastAPI (Python) と yt-dlp を使用した、YouTube動画ダウンロードAPIおよび軽量フロントエンドアプリケーションです。

## 概要

- **完全ステートレス**: サーバー上に動画やデータベースを保持せず、ダウンロード完了後に一時ファイルを自動削除します。
- **cookie認証対応**: ブラウザからエクスポートしたcookieを使用し、ログイン限定・年齢制限動画にも対応します。
- **モダンなUI**: Tailwind CSS を使用したシンプルかつレスポンシブなデザイン。

## 技術スタック

- **Backend**: Python 3.12, FastAPI, yt-dlp, uvicorn, ffmpeg, Node.js(署名解読用)
- **Frontend**: HTML5, JavaScript (Fetch API), Tailwind CSS
- **Container**: Docker / Docker Compose

## ディレクトリ構成
```
.
├── backend/
│ ├── main.py # FastAPI バックエンド処理
│ ├── cookies.txt # YouTube cookie(gitignore対象、各自で用意)
│ ├── Dockerfile
│ ├── docker-compose.yml
│ └── requirements.txt
├── frontend/
│ └── index.html # フロントエンド画面
├── .gitignore
└── README.md
```

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/hisao5232/yt-downloader.git
cd yt-downloader
```

### 2. cookieを準備する

ログイン限定・年齢制限動画をダウンロードするには、ブラウザからエクスポートしたcookieが必要です。

1. Chrome/Edge拡張 [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) をインストール
2. YouTubeにログインした状態で `cookies.txt` としてエクスポート
3. `backend/cookies.txt` に配置

```bash
cp /path/to/cookies.txt backend/cookies.txt
```

### 3. バックエンドを起動(Docker)

```bash
cd backend
docker compose build
docker compose up -d
```

起動確認:

```bash
curl http://localhost:8000/
# {"status":"ok","message":"YouTube Downloader API"}
```

ログ確認:

```bash
docker compose logs -f
```

### 4. フロントエンドを起動

`frontend/index.html` は静的ファイルなので、簡易HTTPサーバーで配信します。

```bash
cd ../frontend
python3 -m http.server 3000
```

### 5. ブラウザでアクセス
http://localhost:3000

WSL環境で `localhost` が開けない場合は、WSLのIPアドレスを使ってアクセスしてください。

```bash
# WSL側でIPアドレスを確認
hostname -I
```

http://<WSLのIPアドレス>:3000

(`.wslconfig` に `localhostForwarding=true` を設定し `wsl --shutdown` で再起動すると `localhost` でアクセスできるようになります)

## 既知の制限

- YouTube側の仕様変更(SABR配信への移行)により、取得できる画質が360p程度に制限される場合があります
- cookieは有効期限が短いため、定期的な再エクスポートが必要です

## 免責事項 (Disclaimer)
本ツールは技術検証および個人学習を目的として作成されています。

YouTubeの利用規約に従ってご利用ください。

違法にアップロードされたコンテンツのダウンロードや、著作権を侵害する行為には使用しないでください。

本ツールの利用によって生じた一切の損害について、制作者は責任を負いません。


---
