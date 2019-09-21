import glob
import pickle

import cv2
import numpy as np

ROBOT_LOG_DIR = "logs/robot"

SIMU_LOG_DIR = "logs/simu"

COMPUTED_LOG_DIR = ROBOT_LOG_DIR

ORIGINAL_LOG_DIR = "logs/original"

TOTAL_LATENCY = 0.10


def find_closest_original_image_file(time):
    last_file = None
    for file_path in glob.glob(ORIGINAL_LOG_DIR + "/*.pickle"):
        time_file = float(file_path.replace(".pickle", "").replace(ORIGINAL_LOG_DIR, "").replace("\\", ""))
        if time_file >= time:
            return file_path
        last_file = file_path
    return last_file


def find_closest_original_frame_in_file(file_path, time):
    with open(file_path, "rb")as file:
        logs_original_images = pickle.load(file)
        times = [log_original_image[0] for log_original_image in logs_original_images]
        nearest_time = min(times, key=lambda x: abs(time - x))
        for original_frame_log in logs_original_images:
            if original_frame_log[0] == nearest_time:
                return original_frame_log[1]


def draw_interpol_poly1(image, poly_coefs):
    def poly1(x):
        return poly_coefs[0] * x + poly_coefs[1]
    shape = image.shape
    xall = np.arange(0, shape[0] - 1)
    ypoly = poly1(xall).astype(int)
    ypoly = np.clip(ypoly, 0, shape[1] - 2)
    image[xall, ypoly, :] = 0
    image[xall, ypoly, 1] = 255
    return image


def find_closest_original_frame(time):
    closest_original_image_frame = find_closest_original_image_file(time)
    return find_closest_original_frame_in_file(closest_original_image_frame, time)


for file_path in glob.glob(COMPUTED_LOG_DIR + "/run_*.pickle"):
    with open(file_path, "rb")as file:
        logs = pickle.load(file)
        print()
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
                final_with_interpol = draw_interpol_poly1(final, poly1_coefs)
                cv2.imshow("final", log[1])
            if log[8] is not None:
                cv2.imshow("perspective", log[8])
            if log[9] is not None:
                cv2.imshow("translated", log[9])
            if log[9] is not None:
                cv2.imshow("rotated", log[10])
            cv2.waitKey(0)
