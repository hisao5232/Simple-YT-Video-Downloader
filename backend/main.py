# main.py
import os
import re
import tempfile
import uuid
from urllib.parse import quote
from fastapi import BackgroundTasks, FastAPI, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import yt_dlp

load_dotenv()

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
API_KEY = os.getenv("API_KEY", "changeme")

# ジョブの状態を保持するメモリ上の辞書
# {job_id: {"status": "downloading"/"success"/"error", "progress": "45.2%", "file_path": ..., "filename": ..., "error": ...}}
jobs: dict[str, dict] = {}


def sanitize_filename(filename: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", filename)


def remove_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"一時ファイルの削除エラー: {e}")


def run_download(job_id: str, url: str):
    """バックグラウンドで実行される実際のダウンロード処理"""
    temp_dir = tempfile.mkdtemp()
    output_template = os.path.join(temp_dir, "%(title)s.%(ext)s")

    def progress_hook(d):
        """yt-dlpから呼ばれる進捗コールバック"""
        if d["status"] == "downloading":
            percent = d.get("_percent_str", "N/A").strip()
            speed = d.get("_speed_str", "N/A").strip()
            eta = d.get("_eta_str", "N/A").strip()
            jobs[job_id]["progress"] = f"{percent} (speed: {speed}, ETA: {eta})"
        elif d["status"] == "finished":
            jobs[job_id]["progress"] = "変換処理中..."

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "bestvideo+bestaudio/best",
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "js_runtimes": {"node": {}},
        "remote_components": ["ejs:github"],
        "extractor_args": {
            "youtube": {
                "player_client": ["visionos", "android", "web"],
            }
        },
        "progress_hooks": [progress_hook],
    }

    if os.path.exists(cookie_file):
        ydl_opts["cookiefile"] = cookie_file

    try:
        jobs[job_id]["status"] = "downloading"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            base, _ = os.path.splitext(filename)
            final_filepath = f"{base}.mp4"
            if not os.path.exists(final_filepath) and os.path.exists(filename):
                final_filepath = filename

            raw_title = info.get("title", "video")

        clean_title = sanitize_filename(raw_title)
        final_filename = f"{clean_title}.mp4"

        jobs[job_id]["status"] = "success"
        jobs[job_id]["progress"] = "100%"
        jobs[job_id]["file_path"] = final_filepath
        jobs[job_id]["filename"] = final_filename
        jobs[job_id]["title"] = clean_title
        jobs[job_id]["temp_dir"] = temp_dir

    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)
        # 失敗時は一時ファイルをクリーンアップ
        if os.path.exists(temp_dir):
            for f in os.listdir(temp_dir):
                try:
                    os.remove(os.path.join(temp_dir, f))
                except Exception:
                    pass
            try:
                os.rmdir(temp_dir)
            except Exception:
                pass


@app.get("/")
def read_root():
    return {"status": "ok", "message": "YouTube Downloader API"}


@app.post("/download/start")
def start_download(
    background_tasks: BackgroundTasks,
    url: str = Query(..., description="YouTube Video URL"),
    x_api_key: str = Header(...),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued", "progress": "0%"}

    background_tasks.add_task(run_download, job_id, url)

    print(f"--- [REQUEST] Started job {job_id} for URL: {url} ---")
    return {"job_id": job_id, "status": "queued"}


@app.get("/download/status/{job_id}")
def get_status(job_id: str, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job.get("progress"),
        "filename": job.get("filename"),
        "error": job.get("error"),
    }


@app.get("/download/result/{job_id}")
def get_result(job_id: str, background_tasks: BackgroundTasks, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "success":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not ready. Current status: {job['status']}"
        )

    final_filepath = job["file_path"]
    final_filename = job["filename"]
    temp_dir = job["temp_dir"]

    print("========================================")
    print("[RESULT]")
    print(f"file_path   : {final_filepath}")
    print(f"filename    : {final_filename}")
    print(f"temp_dir    : {temp_dir}")
    print(f"exists      : {os.path.exists(final_filepath)}")

    if os.path.exists(final_filepath):
        print(f"file_size   : {os.path.getsize(final_filepath)} bytes")
    else:
        print("file_size   : FILE NOT FOUND")

    print("========================================")

    encoded_filename = quote(final_filename)

    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
    }

    background_tasks.add_task(remove_file, final_filepath)
    background_tasks.add_task(os.rmdir, temp_dir)
    background_tasks.add_task(jobs.pop, job_id, None)

    return FileResponse(
        path=final_filepath,
        media_type="video/mp4",
        headers=headers
    )
