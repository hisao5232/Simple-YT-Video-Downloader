import os
import re
import tempfile
from urllib.parse import quote
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yt_dlp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "Content-Disposition"
    ],
)


def sanitize_filename(filename: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", filename)


def remove_file(path: str):
    """レスポンス送信後に一時ファイルを削除する関数"""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"一時ファイルの削除エラー: {e}")


@app.get("/download")
async def download_video(
    background_tasks: BackgroundTasks,
    url: str = Query(..., description="YouTube Video URL"),
):
    # 一時フォルダ内にランダムなファイルを作成
    temp_dir = tempfile.mkdtemp()
    output_template = os.path.join(temp_dir, "%(title)s.%(ext)s")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        # 最高画質の映像と音声を結合してMP4で出力
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": output_template,
        "merge_output_format": "mp4",
    }

    try:
        # 1. yt-dlp で動画・音声を結合して一時フォルダへダウンロード
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            # 拡張子が mp4 でない場合（結合後）のファイルパス調整
            base, _ = os.path.splitext(filename)
            final_filepath = f"{base}.mp4"
            if not os.path.exists(final_filepath) and os.path.exists(
                filename
            ):
                final_filepath = filename

            raw_title = info.get("title", "video")

        clean_title = sanitize_filename(raw_title)
        encoded_filename = quote(f"{clean_title}.mp4")

        # 2. クライアントへのレスポンス完了後に一時ファイルを削除するようにバックグラウンドタスク登録
        background_tasks.add_task(remove_file, final_filepath)
        background_tasks.add_task(os.rmdir, temp_dir)

        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }

        # 3. ファイルを返却
        return FileResponse(
            path=final_filepath, media_type="video/mp4", headers=headers
        )

    except Exception as e:
        # エラー発生時も一時ディレクトリをクリーンアップ
        if os.path.exists(temp_dir):
            for f in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, f))
            os.rmdir(temp_dir)

        raise HTTPException(
            status_code=500, detail=f"エラーが発生しました: {str(e)}"
        )
