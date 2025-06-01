import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def video_file():
    return open("tests/sample.mp4", "rb")

def test_upload_and_extract(video_file):
    # Upload video
    response = client.post("/upload_video", files={"video": video_file})
    assert response.status_code == 200
    video_id = response.json()["video_id"]
    filename = response.json()["saved_as"]

    # Extract frames
    extract_resp = client.post("/extract_frames", params={"video_id": video_id, "filename": filename})
    assert extract_resp.status_code == 200
    assert "frames extracted" in extract_resp.json()["message"]