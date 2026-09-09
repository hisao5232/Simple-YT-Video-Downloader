# main.py
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
    expose_headers=["Content-Disposition"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cookie_file = os.path.join(BASE_DIR, "cookies.txt")

print(f"=== [STARTUP CHECK] Cookie File Path: {cookie_file} ===")
if os.path.exists(cookie_file):
    file_size = os.path.getsize(cookie_file)
    print(f"=== [STARTUP CHECK] SUCCESS: cookies.txt found! Size: {file_size} bytes ===")
else:
    print("=== [STARTUP CHECK] WARNING: cookies.txt NOT found in container! ===")


def sanitize_filename(filename: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", filename)


def remove_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"一時ファイルの削除エラー: {e}")


@app.get("/")
def read_root():
    return {"status": "ok", "message": "YouTube Downloader API"}


@app.get("/download")
async def download_video(
    background_tasks: BackgroundTasks,
    url: str = Query(..., description="YouTube Video URL"),
):
    print(f"--- [REQUEST] Processing download for URL: {url} ---")

    temp_dir = tempfile.mkdtemp()
    output_template = os.path.join(temp_dir, "%(title)s.%(ext)s")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "bestvideo+bestaudio/best",  # 拡張子縛りを外す
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "js_runtimes": {"node": {}},
        "remote_components": ["ejs:github"],
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],  # androidを優先、webはフォールバック
            }
        },
    }

    if os.path.exists(cookie_file):
        size = os.path.getsize(cookie_file)
        print(f"--- [yt-dlp] Using cookie file ({size} bytes): {cookie_file} ---")
        ydl_opts["cookiefile"] = cookie_file
    else:
        print("--- [yt-dlp] WARNING: cookie file is NOT being used (file missing) ---")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            base, _ = os.path.splitext(filename)
            final_filepath = f"{base}.mp4"
            if not os.path.exists(final_filepath) and os.path.exists(filename):
                final_filepath = filename

            raw_title = info.get("title", "video")

        clean_title = sanitize_filename(raw_title)
        encoded_filename = quote(f"{clean_title}.mp4")

        background_tasks.add_task(remove_file, final_filepath)
        background_tasks.add_task(os.rmdir, temp_dir)

        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }

        print("--- [SUCCESS] Download complete, sending file response. ---")
        return FileResponse(
            path=final_filepath, media_type="video/mp4", headers=headers
        )

    except Exception as e:
        print(f"--- [ERROR] Download failed: {str(e)} ---")
        if os.path.exists(temp_dir):
            for f in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, f))
            os.rmdir(temp_dir)

        raise HTTPException(
            status_code=500, detail=f"エラーが発生しました: {str(e)}"
        )
        