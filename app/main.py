import os, shutil, subprocess, tempfile
from threading import Lock
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from starlette.background import BackgroundTask

app = FastAPI(title="SFERA FaceFusion API", version="0.1")
API_TOKEN = os.environ.get("SFERA_API_TOKEN", "")
FF = Path("/opt/facefusion")
GPU_LOCK = Lock()

def auth(authorization: str | None):
    if not API_TOKEN:
        raise HTTPException(503, "SFERA_API_TOKEN is not configured")
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(401, "Unauthorized")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/swap")
def swap(
    face: UploadFile = File(...),
    video: UploadFile = File(...),
    authorization: str | None = Header(default=None)
):
    auth(authorization)
    if not GPU_LOCK.acquire(blocking=False):
        raise HTTPException(429, "GPU is busy; retry later")
    try:
        return run_swap(face, video)
    finally:
        GPU_LOCK.release()

def run_swap(face, video):
    job = Path(tempfile.mkdtemp(prefix="sfera-"))
    src = job / ("face" + (Path(face.filename or "").suffix or ".jpg"))
    target = job / ("target" + (Path(video.filename or "").suffix or ".mp4"))
    out = job / "result.mp4"
    try:
        with src.open("wb") as f: shutil.copyfileobj(face.file, f)
        with target.open("wb") as f: shutil.copyfileobj(video.file, f)
        cmd = [
            "python3", str(FF / "facefusion.py"), "headless-run",
            "--source-paths", str(src),
            "--target-path", str(target),
            "--output-path", str(out),
            "--processors", "face_swapper",
            "--execution-providers", "cuda",
            "--face-swapper-model", os.getenv("FACE_SWAPPER_MODEL","inswapper_128_fp16"),
            "--output-video-encoder", "libx264",
        ]
        p = subprocess.run(cmd, cwd=str(FF), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=int(os.getenv("JOB_TIMEOUT","900")))
        if p.returncode != 0 or not out.exists():
            raise HTTPException(500, detail={"message":"FaceFusion failed","log":p.stdout[-4000:]})
        return FileResponse(out, media_type="video/mp4", filename="sfera-result.mp4",
                            background=BackgroundTask(shutil.rmtree, job, True))
    except subprocess.TimeoutExpired:
        shutil.rmtree(job, ignore_errors=True)
        raise HTTPException(504, "FaceFusion timed out")
    except Exception:
        if job.exists(): shutil.rmtree(job, ignore_errors=True)
        raise
