import cv2

import numpy as np


class ImageWarper:
    def __init__(self, tachometer, gyro):
        self.tacho = tachometer
        self.gyro = gyro

    def warp(self, image):
        height, width = image.shape
        bl = [0, height]
        br = [width, height]
        delta_gyro = self.gyro.get_gyro_variation_step()
        print(delta_gyro)
        pts1 = np.float32([[100, 60], [width - 100, 60], bl, br])
        pts2 = np.float32([[0, 0], [width, 0], bl, br])
        P = cv2.getPerspectiveTransform(pts1, pts2)
        T = np.float32([[1, 0, 0], [0, 1, 25]])
        R = cv2.getRotationMatrix2D((width / 2, height), delta_gyro, 1)
        image = cv2.warpPerspective(image, P, (width, height))
        image = cv2.warpAffine(image, T, (width, height))
        image = cv2.warpAffine(image, R, (width, height))
        image = cv2.warpAffine(image, T, (width, height))
        return image
