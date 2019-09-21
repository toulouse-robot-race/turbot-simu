#!/usr/bin/env python3
import gzip
import os
import pickle
import time
from pathlib import Path

import numpy as np
import tensorflow as tf
from keras.models import load_model

from robot.real.Camera import Camera
from robot.real.UsbCam import UsbCam

MODEL_FILENAME = 'deep_learning/models/final_race_model_5_3.h5'

RAM_DISK_DIR = "/tmp_ram"

INFERENCE_DISABLE_FILE = "inference.disable"

MASK_LINE_FILE = RAM_DISK_DIR + "/mask_line.npy"

MASK_OBSTACLE_FILE = RAM_DISK_DIR + "/mask_obstacle.npy"

MASK_OBSTACLE_FILE_TMP = RAM_DISK_DIR + "/mask_obstacle.tmp.npy"

MASK_LINE_FILE_TMP = RAM_DISK_DIR + "/mask_line.tmp.npy"

LOGS_DIR = "logs/original"

if not os.path.isdir(LOGS_DIR):
    os.makedirs(LOGS_DIR)

SIZE_LOG_FRAMES_STACK = 10

FRAME_CYCLE_LOG = 5

frame_index = 1

log_enabled = True

# Bug fix for tensorflow on TX2
# See here: https://devtalk.nvidia.com/default/topic/1030875/jetson-tx2/gpu-sync-failed-in-tx2-when-running-tensorflow/
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)

# Load model
seq = load_model(MODEL_FILENAME)

usbCam = UsbCam()

cam = Camera(MASK_LINE_FILE, MASK_OBSTACLE_FILE)

frames_to_log = []
while True:
    begin_time = time.time()

    # Check if inference is enabled
    if Path(INFERENCE_DISABLE_FILE).is_file():
        time.sleep(0.1)
        continue

    frame = usbCam.read()

    if log_enabled:
        if (frame_index % FRAME_CYCLE_LOG) == 0:
            frames_to_log.append([time.time(), frame])
            if len(frames_to_log) >= SIZE_LOG_FRAMES_STACK:
                begin_log_time = time.time()
                file_path = LOGS_DIR + "/" + ("%010.5f" % time.time()) + ".pgz"
                with gzip.open(file_path, "w")as file:
                    pickle.dump(frames_to_log, file)
                print("log time", time.time() - begin_log_time)
                frames_to_log.clear()
        frame_index += 1

    # Process inference
    predicted_masks = seq.predict(frame[np.newaxis, :, :, :])[0, ...]
    mask_line = predicted_masks[:, :, 0]
    mask_obstacle = predicted_masks[:, :, 1]

    prediction_time = time.time()

    mask_line = mask_line > 0.1
    mask_obstacle = mask_obstacle > 0.1

    # Save mask in ram disk files
    np.save(MASK_LINE_FILE_TMP, mask_line)
    np.save(MASK_OBSTACLE_FILE_TMP, mask_obstacle)

    os.rename(MASK_LINE_FILE_TMP, MASK_LINE_FILE)
    os.rename(MASK_OBSTACLE_FILE_TMP, MASK_OBSTACLE_FILE)
