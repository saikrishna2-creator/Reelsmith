import pytest
from fastapi.testclient import TestClient
from reelsmith.backend.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_process_reel_success():
    # A simple test to ensure the endpoint returns a jobId
    response = client.post("/processReel", json={
        "videoUrls": ["http://example.com/video.mp4"],
        "musicUrl": "http://example.com/music.mp3",
        "niche": "travel"
    })
    assert response.status_code == 200
    assert "jobId" in response.json()

def test_get_status_not_found():
    response = client.get("/getStatus/non_existent_job_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Job not found"}

# More comprehensive tests would mock the background task
# and verify the job status changes over time.
