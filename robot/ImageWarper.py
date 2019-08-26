import cv2
import numpy as np

PIXELS_METER = 250


class ImageWarper:
    def __init__(self, car, nb_images_delay, tacho_coef, show_and_wait=False,
                 rotation_enabled=True, translation_enabled=True):
        self.translation_enabled = translation_enabled
        self.tacho_coef = tacho_coef
        self.nb_images_delay = nb_images_delay
        self.car = car
        self.rotations = []
        self.translations = []
        self.rotation_enabled = rotation_enabled
        self.show_and_wait = show_and_wait

    def warp(self, image):

        if self.nb_images_delay == 0:
            actives_rotations = []
            actives_translations = []
        else:
            final = self.car.get_delta_cap()
            translation = self.car.get_delta_tacho() / self.tacho_coef * PIXELS_METER
            self.rotations.append(final)
            self.translations.append(translation)

            actives_rotations = self.rotations[-self.nb_images_delay:] if len(
                self.rotations) >= self.nb_images_delay else self.rotations
            actives_translations = self.translations[-self.nb_images_delay:] if len(
                self.rotations) >= self.nb_images_delay else self.translations

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

        warped = cv2.warpPerspective(image, perspective_matrix, (width, height))

        if self.translation_enabled:
            warped = cv2.warpAffine(warped, translation_matrix, (width, height))

        if self.rotation_enabled:
            warped = cv2.warpAffine(warped, rotation_matrix, (width, height))

        if self.show_and_wait:
            cv2.imshow("final", warped)
            cv2.waitKey(0)

        return warped
