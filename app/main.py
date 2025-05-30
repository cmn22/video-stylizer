

from fastapi import FastAPI, UploadFile, File
import os
import uuid

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload_video")
async def upload_video(video: UploadFile = File(...)):
    video_id = str(uuid.uuid4())  # Unique ID to prevent overwrites
    filename = f"{video_id}_{video.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Save file to uploads folder
    with open(file_path, "wb") as f:
        content = await video.read()
        f.write(content)

    return {"message": "Video uploaded successfully", "saved_as": filename}