import cv2
import numpy as np
import os


def cartoonize_frame(image_path: str) -> np.ndarray:
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image at {image_path}")

    # Resize (optional, helps keep output consistent)
    img = cv2.resize(img, (640, 480))

    # Step 1: Bilateral filtering (for smoothing)
    for _ in range(2):
        img = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)

    # Step 2: Convert to grayscale and apply edge detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.adaptiveThreshold(
        cv2.medianBlur(gray, 7), 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        blockSize=9,
        C=2
    )

    # Step 3: Color quantization using k-means clustering
    data = np.float32(img).reshape((-1, 3))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(data, 9, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS) # type: ignore
    quantized = centers[labels.flatten()].reshape(img.shape).astype(np.uint8)

    # Step 4: Combine quantized color image with edge mask
    cartoon = cv2.bitwise_and(quantized, quantized, mask=edges)

    return cartoon


def save_cartoonized_image(input_path: str, output_path: str):
    cartoon = cartoonize_frame(input_path)
    cv2.imwrite(output_path, cartoon)