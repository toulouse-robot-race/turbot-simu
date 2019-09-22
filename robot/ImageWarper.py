import cv2
import numpy as np

PIXELS_METER = 133


class ImageWarper:
    def __init__(self, car, nb_images_delay, tacho_coef, show_and_wait=False,
                 rotation_enabled=True, translation_enabled=True):
        self.translation_enabled = translation_enabled
        self.tacho_coef = tacho_coef
        self.nb_images_delay = nb_images_delay
        self.car = car
        self.rotations = []
        self.translations = []
        self.actives_translations = []
        self.actives_rotations = []
        self.rotation_enabled = rotation_enabled
        self.show_and_wait = show_and_wait
        self.translated = None
        self.rotated = None
        self.perspective = None

    warped_height = 400
    warped_width = 300

    def warp(self, image, type):
        if self.nb_images_delay == 0:
            self.actives_rotations = []
            self.actives_translations = []
        else:
            final = self.car.get_delta_cap()
            translation = self.car.get_delta_tacho() / self.tacho_coef * PIXELS_METER
            self.rotations.append(final)
            self.translations.append(translation)

            self.actives_rotations = self.rotations[-self.nb_images_delay:] if len(
                self.rotations) >= self.nb_images_delay else self.rotations
            self.actives_translations = self.translations[-self.nb_images_delay:] if len(
                self.rotations) >= self.nb_images_delay else self.translations

        translation_to_apply = np.sum(self.actives_translations)
        rotation_to_apply = np.sum(self.actives_rotations)

        # Define a tetrahedron that will become rectangular and take all screen
        h1 = 25         # This parameter sets the distance of vision (if you change this, the image might become a little rectangular. You could need to change resulting image size.)
        h2 = 240        # This parameter sets the beginning of vision distance (near the robot)
        middle = 160
        horizon = -20   # This parameter that needs to be calibrated according to the camera. If it is calibrated, squares should look rectangular. If not, they will look trapezoidal.
        pente = 1.6     # This parameter changes de angle of vision of the reprojection

        tl = np.float32([h1, -(h1 - horizon) * pente + middle])
        tr = np.float32([h1, (h1 - horizon) * pente + middle])
        bl = np.float32([h2, -(h2 - horizon) * pente + middle])
        br = np.float32([h2, (h2 - horizon) * pente + middle])
        pts1 = np.array([tl, tr, bl, br])
        # Convert to openCV coordinates system
        pts1 = pts1[:, ::-1]
        new_height = self.warped_height
        new_width = self.warped_width
        height, width = new_height, new_width
        pts2 = np.float32([[0, 0], [new_width, 0], [0, new_height], [new_width, new_height]])
        perspective_matrix = cv2.getPerspectiveTransform(pts1, pts2)

        translation_matrix = np.float32([[1, 0, 0], [0, 1, translation_to_apply]])
        rotation_matrix = cv2.getRotationMatrix2D((width / 2, height), rotation_to_apply, 1)

        warped = cv2.warpPerspective(image, perspective_matrix, (width, height))

        if type == "line":
            self.perspective = warped.copy()

        if self.translation_enabled:
            warped = cv2.warpAffine(warped, translation_matrix, (width, height))
            if type == "line":
                self.translated = warped.copy()

        if self.rotation_enabled:
            warped = cv2.warpAffine(warped, rotation_matrix, (width, height))
            if type == "line":
                self.rotated = warped.copy()

        if self.show_and_wait:
            cv2.imshow("final", warped)
            cv2.waitKey(0)

        return warped
