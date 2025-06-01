

from fastapi import FastAPI, UploadFile, File, HTTPException
from app.utils import extract_frames
import os
import uuid

app = FastAPI()

UPLOAD_DIR = "uploads"
FRAME_DIR = "frames"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FRAME_DIR, exist_ok=True)

@app.post("/upload_video")
async def upload_video(video: UploadFile = File(...)):
    video_id = str(uuid.uuid4())  # Unique ID to prevent overwrites
    filename = f"{video_id}_{video.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Save file to uploads folder
    with open(file_path, "wb") as f:
        content = await video.read()
        f.write(content)

    return {"message": "Video uploaded successfully", "video_id": video_id, "saved_as": filename}


@app.post("/extract_frames")
def extract(video_id: str, filename: str):
    video_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")

    output_dir = os.path.join(FRAME_DIR, video_id)
    num_frames = extract_frames(video_path, output_dir)

    return {"message": f"{num_frames} frames extracted", "output_dir": output_dir}