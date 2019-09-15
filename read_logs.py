import glob

import cv2
import numpy as np

LOG_DIR = "logs"

ORIGINAL_LOG_DIR = "simu/logs"

TOTAL_LATENCY = 0.10


def find_closest_original_image_file(time):
    last_file = None
    for file in glob.glob(ORIGINAL_LOG_DIR + "/*.npz"):
        time_file = float(file.replace(".npz", "").replace("simu/logs", "").replace("\\", ""))
        if time_file >= time:
            return file
        last_file = file
    return last_file


def find_closest_original_frame_in_file(file, time):
    logs_original_images = np.load(file, allow_pickle=True)["data"]
    times = [log_original_image[0] for log_original_image in logs_original_images]
    nearest_time = min(times, key=lambda x: abs(time - x))
    for original_frame_log in logs_original_images:
        if original_frame_log[0] == nearest_time:
            return original_frame_log[1]


def find_closest_original_frame(time):
    closest_original_image_frame = find_closest_original_image_file(time)
    return find_closest_original_frame_in_file(closest_original_image_frame, time)


for file in glob.glob(LOG_DIR + "/run_0*.npz"):
    logs = np.load(file, allow_pickle=True)["data"]
    for log in logs:
        time = log[0]
        original_frame = find_closest_original_frame(time - TOTAL_LATENCY)
        print("time", time)
        print("poly   coef 1", log[2])
        print("pixel line offset", log[3])
        print("distance_obstacle_line", log[4])
        print("steering", log[5])
        print("actives rotations", log[6])
        print("actives translations", log[7])
        if original_frame is not None:
            cv2.imshow("original", original_frame)
        if log[1] is not None:
            cv2.imshow("final", log[1])
        if log[8] is not None:
            cv2.imshow("perspective", log[8])
        if log[9] is not None:
            cv2.imshow("translated", log[9])
        if log[9] is not None:
            cv2.imshow("rotated", log[10])
        cv2.waitKey(0)
