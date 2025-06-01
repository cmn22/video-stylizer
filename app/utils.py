import cv2
import os
from natsort import natsorted
from app.styler import save_cartoonized_image

BASE_DIR = "data"
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

STYLE_FUNCTIONS = {
    "cartoon": save_cartoonized_image
}


def safe_video_path(video_id_or_filename: str) -> str:
    # Ensure .mp4 extension
    if not video_id_or_filename.endswith(".mp4"):
        video_id_or_filename += ".mp4"
    return os.path.join(UPLOAD_DIR, video_id_or_filename)


def extract_frames(video_path: str, output_dir: str):
    output_dir = os.path.join(BASE_DIR, output_dir)
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    
    count = 0
    while True:
        success, frame = cap.read()
        if not success:
            break
        frame_path = os.path.join(output_dir, f"frame_{count:05d}.jpg")
        cv2.imwrite(frame_path, frame)
        count += 1

    cap.release()
    return count  # Number of frames extracted


def frames_to_video(frames_dir: str, output_path: str, fps: int = 24):
    frames_dir = os.path.join(BASE_DIR, frames_dir)
    output_path = os.path.join(BASE_DIR, output_path)

    frames = natsorted([
        f for f in os.listdir(frames_dir)
        if f.lower().endswith((".jpg", ".png"))
    ])

    if not frames:
        raise ValueError("No frames found to create video.")

    first_frame_path = os.path.join(frames_dir, frames[0])
    first_frame = cv2.imread(first_frame_path)
    height, width, _ = first_frame.shape

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # type: ignore
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for frame_name in frames:
        frame_path = os.path.join(frames_dir, frame_name)
        frame = cv2.imread(frame_path)
        out.write(frame)

    out.release()