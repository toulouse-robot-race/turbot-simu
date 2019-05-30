import cv2

import numpy as np

T_COEFF = 1
R_COEFF = 1

class ImageWarper:
    def __init__(self, tachometer, gyro):
        self.tacho = tachometer
        self.gyro = gyro

    def warp(self, image):
        height, width = image.shape
        bl = [0, height]
        br = [width, height]
        rotation = self.gyro.get_delta_cap() * R_COEFF
        translation = self.tacho.get_delta_tacho() * T_COEFF
        pts1 = np.float32([[100, 60], [width - 100, 60], bl, br])
        pts2 = np.float32([[0, 0], [width, 0], bl, br])
        P = cv2.getPerspectiveTransform(pts1, pts2)
        T = np.float32([[1, 0, 0], [0, 1, translation/2]])
        R = cv2.getRotationMatrix2D((width / 2, height), rotation, 1)
        perspective = cv2.warpPerspective(image, P, (width, height))
        cv2.imshow("perspective", perspective)
        translation = cv2.warpAffine(perspective, T, (width, height))
        cv2.imshow("translation1", translation)
        rotation = cv2.warpAffine(translation, R, (width, height))
        cv2.imshow("rotation", rotation)
        translation2 = cv2.warpAffine(rotation, T, (width, height))
        cv2.imshow("translation2", translation2)
        cv2.waitKey(0)
        return translation2
