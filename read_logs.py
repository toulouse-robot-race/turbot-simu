import glob
import gzip
import os
import pickle

import cv2

from robot.ImageAnalyzer import draw_interpol_poly1

ROBOT_LOG_DIR = "logs/robot"

SIMU_LOG_DIR = "logs/simu"

COMPUTED_LOG_DIR = ROBOT_LOG_DIR

ORIGINAL_LOG_DIR = "logs/original"

TOTAL_LATENCY = 0.10


def open_log_file(file_path):
    ext = os.path.splitext(file_path)[1]
    if ext == ".pickle":
        return open(file_path, "rb")
    elif ext == ".pgz":
        return gzip.open(file_path, "r")
    else:
        return None


def find_closest_original_image_file(time):
    last_file = None
    for file_path in sorted(glob.glob(ORIGINAL_LOG_DIR + "/*"), key=lambda x: os.path.splitext(x)[0]):
        time_file = float(file_path.replace(os.path.splitext(file_path)[1], "")
                          .replace(ORIGINAL_LOG_DIR + "/", "")
                          .replace(ORIGINAL_LOG_DIR, "")
                          .replace("\\", ""))
        if time_file >= time:
            print(file_path)
            return file_path
        last_file = file_path
    return last_file


def find_closest_original_frame_in_file(file_path, time):
    with open_log_file(file_path)as file:
        logs_original_images = pickle.load(file)
        times = [log_original_image[0] for log_original_image in logs_original_images]
        nearest_time = min(times, key=lambda x: abs(time - x))
        for original_frame_log in logs_original_images:
            if original_frame_log[0] == nearest_time:
                return original_frame_log[1]


def find_closest_original_frame(time):
    closest_original_image_frame = find_closest_original_image_file(time)
    return find_closest_original_frame_in_file(closest_original_image_frame, time)


for file_path in sorted(glob.glob(COMPUTED_LOG_DIR + "/run_*"), key=lambda x: os.path.splitext(x)[0]):
    print("\n")
    print("\n")
    print(file_path)
    with open_log_file(file_path)as file:
        logs = pickle.load(file)
        for log in logs:
            time = log[0]
            original_frame = find_closest_original_frame(time - TOTAL_LATENCY)
            print("time", time)
            poly1_coefs = log[2]
            print("poly   coef 1", log[2])
            print("pixel line offset", log[3])
            print("distance_obstacle_line", log[4])
            print("steering", log[5])
            print("actives rotations", log[6])
            print("actives translations", log[7])
            if original_frame is not None:
                cv2.imshow("original", original_frame)
            if log[1] is not None:
                final = log[1]
                if poly1_coefs is not None:
                    final_with_interpol = draw_interpol_poly1(final, poly1_coefs)
                cv2.imshow("final", log[1])
            if log[8] is not None:
                cv2.imshow("perspective", log[8])
            if log[9] is not None:
                cv2.imshow("translated", log[9])
            if log[9] is not None:
                cv2.imshow("rotated", log[10])
            cv2.waitKey(0)
