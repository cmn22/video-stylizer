import cv2
import os

def extract_frames(video_path: str, output_dir: str):
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