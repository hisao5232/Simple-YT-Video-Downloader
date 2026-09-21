# YouTube Video Downloader

FastAPI（Python）と yt-dlp を使用した、YouTube動画ダウンロードAPIおよび軽量フロントエンドアプリケーションです。

YouTube動画のURLを指定すると、バックエンドで動画をダウンロード・MP4へ変換し、YouTubeのタイトルをファイル名として取得できます。

## 概要

* **非同期ダウンロード**
  ダウンロード開始後はジョブIDで進捗を確認できます。

* **YouTubeタイトルをファイル名に使用**
  ダウンロードした動画は、YouTubeのタイトルを使用したMP4ファイルとして保存されます。日本語タイトルにも対応しています。

* **一時ファイル方式**
  サーバー上ではダウンロード処理中のみ一時ディレクトリに動画を保持し、ダウンロード完了後にクライアントへ転送した後、自動的に削除します。

* **cookie認証対応**
  ブラウザからエクスポートしたcookieを使用して、ログインが必要な動画などの取得に対応します。

* **APIキー認証**
  ダウンロードAPIへのアクセスにはAPIキーを使用します。

* **モダンなUI**
  Tailwind CSSを使用したシンプルでレスポンシブなフロントエンドを用意しています。

* **Docker対応**
  バックエンドはDocker / Docker Composeで簡単に構築できます。

## 動作イメージ

```text
Browser
   │
   │ YouTube URL
   ▼
Frontend
   │
   │ API request
   ▼
FastAPI
   │
   │ Job ID発行
   ▼
yt-dlp
   │
   │ YouTubeから動画を取得
   ▼
一時ディレクトリ
   │
   │ MP4生成
   ▼
FastAPI
   │
   │ 動画ファイルを返却
   ▼
Browser
   │
   └── YouTubeタイトル.mp4

※ ダウンロード完了後、一時ファイルは削除
```

## 技術スタック

### Backend

* Python 3.12
* FastAPI
* Uvicorn
* yt-dlp
* FFmpeg
* Node.js（YouTubeのJavaScript処理用）
* python-dotenv

### Frontend

* HTML5
* JavaScript
* Fetch API
* Tailwind CSS

### Container

* Docker
* Docker Compose

## ディレクトリ構成

```text
.
├── backend/
│   ├── main.py              # FastAPIバックエンド
│   ├── cookies.txt          # YouTube cookie（Git管理対象外）
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
│
├── frontend/
│   └── index.html           # フロントエンド
│
├── download.sh              # CLIから動画をダウンロードするスクリプト
├── .gitignore
└── README.md
```

## API

### 1. ダウンロード開始

```text
POST /download/start
```

YouTube URLを指定してダウンロードジョブを開始します。

```bash
curl -X POST --get \
  "http://localhost:8000/download/start" \
  --data-urlencode "url=https://youtu.be/VIDEO_ID" \
  -H "x-api-key: YOUR_API_KEY"
```

レスポンス例：

```json
{
  "job_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "status": "queued"
}
```

### 2. ダウンロード状況確認

```text
GET /download/status/{job_id}
```

ジョブIDを指定すると、現在の状態と進捗を取得できます。

```json
{
  "job_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "status": "downloading",
  "progress": "89.3% (speed: 36.06MiB/s, ETA: 00:00)"
}
```

ダウンロード完了後：

```json
{
  "job_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "status": "success",
  "progress": "100%",
  "filename": "YouTube動画タイトル.mp4"
}
```

### 3. 動画取得

```text
GET /download/result/{job_id}
```

ダウンロードが完了したジョブから動画ファイルを取得します。

日本語などのUnicode文字を含むタイトルにも対応しています。

```text
【動画タイトル】日本語の動画.mp4
```

動画の転送が完了すると、サーバー上の一時ファイルは削除されます。

## APIキーの設定

バックエンドではAPIキーによる簡易認証を使用しています。

環境変数にAPIキーを設定してください。

```bash
API_KEY=your-secret-api-key
```

実際のAPIキーはGitHubなどの公開リポジトリへコミットしないでください。

## cookieを準備する

ログインが必要な動画などをダウンロードする場合は、ブラウザからエクスポートしたcookieを使用できます。

### 1. 拡張機能をインストール

Chrome / Edgeなどで、`Get cookies.txt LOCALLY` などのcookieエクスポート拡張機能を使用します。

### 2. YouTubeへログイン

ブラウザでYouTubeへログインした状態でcookieをエクスポートします。

### 3. `cookies.txt` として保存

以下の場所に配置します。

```text
backend/cookies.txt
```

例：

```bash
cp /path/to/cookies.txt backend/cookies.txt
```

`cookies.txt` はGit管理対象外にしてください。

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/hisao5232/yt-downloader.git
cd yt-downloader
```

### 2. cookieを配置

必要に応じて、

```text
backend/cookies.txt
```

へcookieファイルを配置します。

cookieを使用しない場合は、ファイルを配置しなくても構いません。

### 3. バックエンドを起動

```bash
cd backend
docker compose up -d --build
```

コンテナの状態を確認します。

```bash
docker compose ps
```

### 4. APIの動作確認

```bash
curl http://localhost:8000/
```

正常に起動していれば、以下のようなレスポンスが返ります。

```json
{
  "status": "ok",
  "message": "YouTube Downloader API"
}
```

### 5. ログを確認

```bash
docker compose logs -f
```

特定のサービスだけ確認する場合：

```bash
docker compose logs -f yt-downloader
```

## CLIからダウンロード

付属の `download.sh` を使用すると、ターミナルから動画をダウンロードできます。

プロジェクトルートから実行：

```bash
./download.sh "https://youtu.be/VIDEO_ID"
```

実行すると、

```text
Job started: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Status: downloading | Progress: 17.6%
Status: downloading | Progress: 89.3%
Status: success | Progress: 100%
Filename: YouTube動画タイトル.mp4
Downloading video...
Download complete!
Saved as: YouTube動画タイトル.mp4
```

のように進捗が表示されます。

## フロントエンドを起動

`frontend/index.html` は静的HTMLファイルとして動作するため、簡易HTTPサーバーで配信できます。

バックエンドとは別のターミナルで実行します。

```bash
cd frontend
python3 -m http.server 3000
```

ブラウザからアクセス：

```text
http://localhost:3000
```

### WSL環境の場合

WSLのIPアドレスを確認できます。

```bash
hostname -I
```

例えば、

```text
172.xx.xx.xx
```

と表示された場合、

```text
http://172.xx.xx.xx:3000
```

でアクセスできます。

Windows側から `localhost` でアクセスできない場合は、WSLのネットワーク設定を確認してください。

## Docker構成

バックエンドはDockerコンテナ内で動作します。

```text
Docker Compose
      │
      ▼
┌──────────────────────┐
│  yt-downloader       │
│                      │
│  FastAPI             │
│  yt-dlp              │
│  FFmpeg              │
│  Node.js             │
│                      │
│  :8000               │
└──────────────────────┘
```

動画はコンテナ内の一時ディレクトリへ保存され、処理完了後にクライアントへ転送されます。

## ダウンロード処理の流れ

```text
① YouTube URLを送信
        ↓
② FastAPIがジョブIDを発行
        ↓
③ バックグラウンドでyt-dlpを実行
        ↓
④ YouTube動画をダウンロード
        ↓
⑤ FFmpegでMP4へ変換
        ↓
⑥ YouTubeタイトルをファイル名として設定
        ↓
⑦ /download/status/{job_id} で完了を確認
        ↓
⑧ /download/result/{job_id} から動画を取得
        ↓
⑨ 一時ファイルを削除
```

## 既知の制限

* YouTube側の仕様変更により、取得できるフォーマットや画質が変化する場合があります。
* YouTube側のSABR配信などの仕様により、高画質フォーマットを取得できない場合があります。
* cookieの有効期限やYouTube側の認証仕様変更により、cookieの再取得が必要になる場合があります。
* YouTube側のbot対策などにより、動画を取得できない場合があります。
* 動画のダウンロードには、動画サイズやネットワーク速度に応じた時間がかかります。
* 本アプリケーションはYouTube側の仕様変更によって動作しなくなる可能性があります。

## セキュリティ上の注意

`cookies.txt` にはYouTubeアカウントの認証情報が含まれる場合があります。

そのため、以下を必ず守ってください。

* `cookies.txt` をGitHubへ公開しない
* `.gitignore` に `cookies.txt` を追加する
* APIキーをGitHubへ公開しない
* APIをインターネットへ公開する場合は、追加のアクセス制御を検討する

`.gitignore` の例：

```text
backend/cookies.txt
.env
__pycache__/
*.pyc
```

## 免責事項（Disclaimer）

本ツールは技術検証および個人学習を目的として作成しています。

YouTubeの利用規約および各コンテンツの権利関係を確認したうえで、適切に利用してください。

違法にアップロードされたコンテンツのダウンロードや、著作権を侵害する目的で使用しないでください。

本ツールの利用によって生じた損害について、制作者は責任を負いません。

## License

This project is provided for personal learning and technical experimentation.
