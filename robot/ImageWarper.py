import cv2

import numpy as np

T_COEFF = 2.3
R_COEFF = 3


class ImageWarper:
    def __init__(self, tachometer, gyro):
        self.tacho = tachometer
        self.gyro = gyro

    def warp(self, image):
        rotation = self.gyro.get_delta_cap() * R_COEFF
        translation = self.tacho.get_delta_tacho() * T_COEFF

        # Define a tetrahedron that will become rectangular and take all screen
        h1 = 50
        h2 = 240
        middle = 160
        horizon = 6
        pente = 2

        tl = np.float32([h1, -(h1 - horizon) * pente + middle])
        tr = np.float32([h1,  (h1 - horizon) * pente + middle])
        bl = np.float32([h2, -(h2 - horizon) * pente + middle])
        br = np.float32([h2,  (h2 - horizon) * pente + middle])
        pts1 = np.array([tl, tr, bl, br])
        # Convert to openCV coordinates system
        pts1 = pts1[:,::-1]
        new_height = 400
        new_width = 300
        height, width = new_height, new_width
        pts2 = np.float32([[0,0],[new_width,0],[0,new_height],[new_width,new_height]])
        perspective_matrix = cv2.getPerspectiveTransform(pts1,pts2)

        translation_matrix = np.float32([[1, 0, 0], [0, 1, translation / 2 ]])
        rotation_matrix = cv2.getRotationMatrix2D((width / 2, height), rotation , 1)

        cv2.imshow("original", image)

        perspective = cv2.warpPerspective(image, perspective_matrix, (width, height))
        cv2.imshow("perspective", perspective)
        translation = cv2.warpAffine(perspective, translation_matrix, (width, height))
        cv2.imshow("translation1", translation)
        rotation = cv2.warpAffine(translation, rotation_matrix, (width, height))
        cv2.imshow("rotation", rotation)
        translation2 = cv2.warpAffine(rotation, translation_matrix, (width, height))
        cv2.imshow("translation2", translation2)

        perspective_matrix_inverse = cv2.getPerspectiveTransform(pts2, pts1)
        perspective_inverse = cv2.warpPerspective(translation2, perspective_matrix_inverse, (320, 240))
        cv2.imshow("persp corrigee", perspective_inverse)

        cv2.waitKey(0)

        return perspective_inverse
