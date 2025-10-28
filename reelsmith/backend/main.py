from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from .utils.job_manager import job_manager
from .utils.reel_processing import process_reel_task

app = FastAPI()

class ReelRequest(BaseModel):
    videoUrls: List[str]
    musicUrl: str
    niche: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/processReel")
async def process_reel(reel_request: ReelRequest, background_tasks: BackgroundTasks):
    job_id = job_manager.create_job()
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
