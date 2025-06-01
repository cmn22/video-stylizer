import os
from app.styler import cartoonize_frame
import cv2

def test_cartoonize_frame_output_shape():
    sample_path = "tests/sample.jpg"
    cartoon = cartoonize_frame(sample_path)
    assert cartoon is not None
    assert len(cartoon.shape) == 3
    assert cartoon.shape[2] == 3