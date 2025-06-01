from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from app.utils import extract_frames, safe_video_path, frames_to_video, STYLE_FUNCTIONS
import os
import uuid
import shutil

app = FastAPI()

UPLOAD_DIR = "uploads"
FRAME_DIR = "frames"
STYLE_DIR = "styled_frames"
folders = ["uploads", "frames", "styled_frames", "styled_videos"]

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FRAME_DIR, exist_ok=True)
os.makedirs(STYLE_DIR, exist_ok=True)

@app.post("/upload_video")
async def upload_video(video: UploadFile = File(...)):
    video_id = str(uuid.uuid4())  # Unique ID to prevent overwrites
    filename = f"{video_id}.mp4"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Save file to uploads folder
    with open(file_path, "wb") as f:
        content = await video.read()
        f.write(content)

    return {"message": "Video uploaded successfully", "video_id": video_id, "saved_as": filename}


@app.post("/extract_frames")
def extract(video_id: str):
    video_path = safe_video_path(video_id)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found")

    output_dir = os.path.join(FRAME_DIR, video_id)
    num_frames = extract_frames(video_path, output_dir)

    return {"message": f"{num_frames} frames extracted", "output_dir": output_dir}


@app.post("/style_frame")
def style_single_frame(video_id: str, frame_name: str, style: str):
    if style not in STYLE_FUNCTIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported style: {style}")

    input_path = os.path.join(FRAME_DIR, video_id, frame_name)
    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail="Frame not found")

    output_dir = os.path.join(STYLE_DIR, video_id, style)
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, frame_name)
    STYLE_FUNCTIONS[style](input_path, output_path)

    return {"message": f"Frame styled as {style}", "output": output_path}


@app.post("/style_frames")
def style_all_frames(video_id: str, style: str):
    if style not in STYLE_FUNCTIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported style: {style}")

    input_dir = os.path.join(FRAME_DIR, video_id)
    output_dir = os.path.join(STYLE_DIR, video_id, style)
    os.makedirs(output_dir, exist_ok=True)

    frame_files = sorted(f for f in os.listdir(input_dir) if f.endswith(".jpg"))
    if not frame_files:
        raise HTTPException(status_code=404, detail="No frames found for video")

    for fname in frame_files:
        input_path = os.path.join(input_dir, fname)
        output_path = os.path.join(output_dir, fname)
        STYLE_FUNCTIONS[style](input_path, output_path)

    return {
        "message": f"All frames styled with '{style}'",
        "styled_dir": output_dir,
        "styled_frames": frame_files
    }


@app.post("/create_stylized_video")
def create_stylized_video(video_id: str, style: str):
    input_dir = os.path.join("styled_frames", video_id, style)
    output_path = os.path.join("styled_videos", video_id, f"{style}.mp4")

    if not os.path.exists(input_dir):
        raise HTTPException(status_code=404, detail="Styled frames not found")

    try:
        frames_to_video(input_dir, output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": f"{style} video created successfully",
        "video_path": output_path
    }


@app.get("/download_video")
def download_video(video_id: str, style: str):
    file_path = os.path.join("styled_videos", video_id, f"{style}.mp4")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Styled video not found")
    return FileResponse(path=file_path, media_type="video/mp4", filename=f"{video_id}_{style}.mp4")


# Download a single styled frame
@app.get("/download_frame")
def download_frame(video_id: str, style: str, frame_name: str):
    file_path = os.path.join("styled_frames", video_id, style, frame_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Styled frame not found")
    return FileResponse(path=file_path, media_type="image/jpeg", filename=frame_name)


@app.delete("/delete_video")
def delete_video(video_id: str):
    deleted = []

    for folder in folders:
        path = os.path.join(folder, video_id)

        # Case: entire subdirectory exists
        if os.path.exists(path) and os.path.isdir(path):
            shutil.rmtree(path)
            deleted.append(path)

        # Special case: uploads contains files, not dirs
        elif folder == "uploads":
            for f in os.listdir("uploads"):
                if f.startswith(video_id):
                    file_path = os.path.join("uploads", f)
                    os.remove(file_path)
                    deleted.append(file_path)

    if not deleted:
        raise HTTPException(status_code=404, detail="No matching files found.")
    
    return {"message": "Deleted resources", "deleted": deleted}


@app.delete("/delete_all")
def delete_all():
    for folder in folders:
        for item in os.listdir(folder):
            path = os.path.join(folder, item)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
    return {"message": "All files and folders deleted from uploads, frames, styled_frames, and styled_videos"}