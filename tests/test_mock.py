from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

@pytest.fixture
def video_file():
    return open("tests/sample.mp4", "rb")

def test_full_pipeline(video_file):
    # Upload
    upload = client.post("/upload_video", files={"video": video_file})
    assert upload.status_code == 200
    vid_id = upload.json()["video_id"]
    fname = upload.json()["saved_as"]

    # Extract
    extract = client.post("/extract_frames", params={"video_id": vid_id, "filename": fname})
    assert extract.status_code == 200

    # Stylize
    style = client.post(f"/style_frames", params={"video_id": vid_id, "style": "cartoon"})
    assert style.status_code == 200
    assert "styled with" in style.json()["message"]

    # Generate video
    gen_vid = client.post(f"/create_stylized_video", params={"video_id": vid_id, "style": "cartoon"})
    assert gen_vid.status_code == 200
    assert gen_vid.json()["video_path"].endswith(".mp4")