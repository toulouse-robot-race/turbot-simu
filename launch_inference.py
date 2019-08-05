#!/usr/bin/env python3
import time
from pathlib import Path

import cv2
import numpy as np
import tensorflow as tf
from keras.models import load_model

from robot.real.Camera import Camera

MODEL_FILENAME = 'deep_learning/models/grs_furby_with_data_augmentation.h5'

RAM_DISK_DIR = "/tmp_ram"

INFERENCE_DISABLE_FILE = "inference.disable"

MASK_LINE_FILE = RAM_DISK_DIR + "/mask_line.npy"

MASK_OBSTACLE_FILE = RAM_DISK_DIR + "/mask_obstacle.npy"

CAM_HANDLE = 1

# Bug fix for tensorflow on TX2
# See here: https://devtalk.nvidia.com/default/topic/1030875/jetson-tx2/gpu-sync-failed-in-tx2-when-running-tensorflow/
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)

# Load model
seq = load_model(MODEL_FILENAME)

# Init camera stream
stream = cv2.VideoCapture(CAM_HANDLE)
stream.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

cam = Camera(MASK_LINE_FILE, MASK_OBSTACLE_FILE)

while True:
    begin_time = time.time()

    # Check if inference is enabled
    if Path(INFERENCE_DISABLE_FILE).is_file():
        time.sleep(0.1)
        continue

    _, frame = stream.read()

    # Process inference
    predicted_masks = seq.predict(frame[np.newaxis, :, :, :])[0, ...]
    mask_line = predicted_masks[:, :, 0]
    mask_obstacle = predicted_masks[:, :, 1]

    prediction_time = time.time()

    mask_line = mask_line > 0.1
    mask_obstacle = mask_obstacle > 0.1

    # Save mask in ram disk files
    np.save(MASK_LINE_FILE, mask_line)
    np.save(MASK_OBSTACLE_FILE, mask_obstacle)

    saving_time = time.time()

    cam.execute()

    reading_time = time.time()

    print("prediction_time", prediction_time - begin_time)
    print("saving_time", saving_time - prediction_time)
    print("reading_time", reading_time - saving_time)

    cv2.imshow("mask obstacle", cam.mask_obstacle)
    cv2.waitKey(1)
