import cv2
import numpy as np

from robot.Config import TACHO_COEF, NB_IMAGES_DELAY

PIXELS_METER = 250


class ImageWarper:
    def __init__(self, car, show_and_wait=False, rotation_enabled=True):
        self.car = car
        self.rotations = []
        self.translations = []
        self.rotation_enabled = rotation_enabled
        self.show_and_wait = show_and_wait

    def warp(self, image):
        final = self.car.get_delta_cap()
        translation = self.car.get_delta_tacho() / TACHO_COEF * PIXELS_METER
        self.rotations.append(final)
        self.translations.append(translation)

        if NB_IMAGES_DELAY == 0:
            actives_rotations = []
            actives_translations = []
        else:
            actives_rotations = self.rotations[-NB_IMAGES_DELAY:] if len(
                self.rotations) >= NB_IMAGES_DELAY else self.rotations
            actives_translations = self.translations[-NB_IMAGES_DELAY:] if len(
                self.rotations) >= NB_IMAGES_DELAY else self.translations

        print("actives_translations", actives_translations)
        translation_to_apply = np.sum(actives_translations)
        rotation_to_apply = np.sum(actives_rotations)

        # Define a tetrahedron that will become rectangular and take all screen
        h1 = 45
        h2 = 240
        middle = 160
        horizon = 6
        pente = 1.8

        tl = np.float32([h1, -(h1 - horizon) * pente + middle])
        tr = np.float32([h1, (h1 - horizon) * pente + middle])
        bl = np.float32([h2, -(h2 - horizon) * pente + middle])
        br = np.float32([h2, (h2 - horizon) * pente + middle])
        pts1 = np.array([tl, tr, bl, br])
        # Convert to openCV coordinates system
        pts1 = pts1[:, ::-1]
        new_height = 400
        new_width = 300
        height, width = new_height, new_width
        pts2 = np.float32([[0, 0], [new_width, 0], [0, new_height], [new_width, new_height]])
        perspective_matrix = cv2.getPerspectiveTransform(pts1, pts2)

        translation_matrix = np.float32([[1, 0, 0], [0, 1, translation_to_apply]])
        rotation_matrix = cv2.getRotationMatrix2D((width / 2, height), rotation_to_apply, 1)
        # cv2.imshow("original", image)

        perspective = cv2.warpPerspective(image, perspective_matrix, (width, height))
        # cv2.imshow("perspective", perspective)

        translation = cv2.warpAffine(perspective, translation_matrix, (width, height))
        # cv2.imshow("translation1", translation)

        if self.rotation_enabled:
            final = cv2.warpAffine(translation, rotation_matrix, (width, height))
            # cv2.imshow("rotation", rotation)
        else:
            final = translation

        if self.show_and_wait:
            cv2.imshow("final", final)
            cv2.waitKey(0)

        return final
