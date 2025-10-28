import os
import shutil
from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from .utils.job_manager import job_manager
from .utils.reel_processing import process_reel_task

# --- App Configuration ---
app = FastAPI()

# --- CORS Middleware ---
# Allow requests from the frontend development server
origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static File Serving ---
UPLOADS_DIR = "reelsmith/backend/uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# --- Pydantic Models ---
class ReelRequest(BaseModel):
    videoUrls: List[str]
    musicUrl: str
    niche: str

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/upload")
async def upload_files(videoFile: UploadFile = File(...), musicFile: UploadFile = File(...)):
    """
    Handles uploading of video and music files.
    Saves them to the server and returns their URLs.
    """
    try:
        video_path = os.path.join(UPLOADS_DIR, videoFile.filename)
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(videoFile.file, buffer)

        music_path = os.path.join(UPLOADS_DIR, musicFile.filename)
        with open(music_path, "wb") as buffer:
            shutil.copyfileobj(musicFile.file, buffer)

        # Construct the URLs. This assumes the backend is running on localhost:8000
        # In a production environment, this would need to be the public URL of the server.
        base_url = "http://localhost:8000"
        video_url = f"{base_url}/uploads/{videoFile.filename}"
        music_url = f"{base_url}/uploads/{musicFile.filename}"

        return {"videoUrl": video_url, "musicUrl": music_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")

@app.post("/processReel")
async def process_reel(reel_request: ReelRequest, background_tasks: BackgroundTasks):
    job_id = job_manager.create_job()
    # For simplicity in this example, we pass a single video URL.
    # The `process_reel_task` expects a list, so we wrap it.
    background_tasks.add_task(
        process_reel_task,
        job_id,
        reel_request.videoUrls,
        reel_request.musicUrl,
        reel_request.niche
    )
    return {"jobId": job_id}

@app.get("/getStatus/{jobId}")
def get_status(jobId: str) -> Dict[str, Any]:
    job = job_manager.get_job_status(jobId)
    if job["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Job not found")
    return job
