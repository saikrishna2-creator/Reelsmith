import pytest
from fastapi.testclient import TestClient
import os
from reelsmith.backend.main import app

client = TestClient(app)

def test_upload_files():
    # Create dummy files to upload
    with open("test_video.mp4", "wb") as f:
        f.write(b"dummy video content")
    with open("test_music.mp3", "wb") as f:
        f.write(b"dummy music content")

    with open("test_video.mp4", "rb") as video_file, open("test_music.mp3", "rb") as music_file:
        response = client.post(
            "/upload",
            files={"videoFile": ("test_video.mp4", video_file, "video/mp4"),
                   "musicFile": ("test_music.mp3", music_file, "audio/mpeg")}
        )

    # Clean up the dummy files
    os.remove("test_video.mp4")
    os.remove("test_music.mp3")

    assert response.status_code == 200
    data = response.json()
    assert "videoUrl" in data
    assert "musicUrl" in data
    assert data["videoUrl"].endswith("/uploads/test_video.mp4")
    assert data["musicUrl"].endswith("/uploads/test_music.mp3")
