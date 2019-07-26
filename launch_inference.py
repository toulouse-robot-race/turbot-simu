import time
from pathlib import Path

import cv2
import numpy as np
from keras.models import load_model

MODEL_FILENAME = 'deep_learning_models/final_race_model_5_3.h5'

RAM_DISK_DIR = "./"

INFERENCE_DISABLE_FILE = "inference.disable"

MASK_LINE_FILE = "mask_line"

MASK_OBSTACLE_FILE = "mask_line"

CAM_HANDLE = 1

# Load model
seq = load_model(MODEL_FILENAME)

# Init camera stream
stream = cv2.VideoCapture(CAM_HANDLE)
stream.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

while True:
    # Check if inference is enabled
    if Path(INFERENCE_DISABLE_FILE).is_file():
        time.sleep(0.1)
        continue

    _, frame = stream.read()

    # Process inference
    predicted_masks = seq.predict(frame[np.newaxis, :, :, :])[0, ...]
    mask_line = predicted_masks[:, :, 0]
    mask_obstacles = predicted_masks[:, :, 1]

    # Save mask in ram disk files
    np.save(MASK_LINE_FILE, mask_line)
    np.save(MASK_OBSTACLE_FILE, mask_obstacles)

