# coding=utf-8
from __future__ import print_function
import numpy as np

import cv2


class ImageAnalyser:
    # Constants for cleaning inference results. IMPORTANT to recalibrate this on real conditions track.
    MIN_AREA_RATIO = 0.35  # if area / area_of_biggest_contour is less than this ratio, contour is bad
    MIN_AREA_TO_KEEP = 100.  # if max_area if less than this, reject all image
    MIN_THRESHOLD_CONTOUR = 10
    MAX_VALUE_CONTOUR = 255

    # Initialisation de la position de la ligne (evite crash si pas de ligne detectee au lancement)
    position_ligne_1 = 0.
    position_ligne_2 = 0.
    poly_coeff = None

    def __init__(self, simulator, cam_handle):
        self.cam_handle = cam_handle
        self.simulator = simulator

    def analyse_image(self):
        resolution, byte_array_image_string = self.simulator.get_gray_image(self.cam_handle)
        mask0 = self.convert_image_to_numpy(byte_array_image_string, resolution)
        mask0 = self.clean_mask(mask0)
        self.position_ligne_1, self.position_ligne_2, self.poly_coeff = self.get_ecart_ligne(mask0)
        print("Position lignes: {:.2f} {:.2f} Poly_coeff_square: {:.4f}".format(self.position_ligne_1,
                                                                                self.position_ligne_2,
                                                                                self.poly_coeff))

    def convert_image_to_numpy(self, byte_array_image_string, resolution):
        return np.flipud(np.fromstring(byte_array_image_string, dtype=np.uint8).reshape(resolution[::-1]))

    def clean_mask(self, image):

        # Scale to openCV format: transform [0.,1.] to [0,255]
        int_mat = (image * 255).astype(np.uint8)

        # Get contours
        _, thresh = cv2.threshold(int_mat, self.MIN_THRESHOLD_CONTOUR, self.MAX_VALUE_CONTOUR, 0)
        _, contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            # No contours, no need to remove anything
            return image
        else:
            # Compute areas of contours
            areas = []
            for cnt in contours:
                areas.append(cv2.contourArea(cnt))

            # Find bad contours
            bad_indexes = []
            max_area = np.max(areas)
            for i, cnt in enumerate(contours):
                # Check if area if too small, in this case, reject contour
                area = areas[i]
                if (area / max_area) < self.MIN_AREA_RATIO:
                    bad_indexes.append(i)
                else:
                    # Compute sum of pixels on area
                    mask = np.ones(int_mat.shape[:2], dtype="uint8") * 255
                    cv2.drawContours(mask, [cnt], -1, 0, -1)
                    # extractMat = np.multiply(image, mask > 0)
                    # sumContour = np.multiply(extractMat, mask > 0).sum()
                    # print("Sum contour {:d}: {:.1f}".format(i, sumContour))

            bad_contours = [contours[i] for i in bad_indexes]

            # Create mask with contours to remove
            mask = np.ones(int_mat.shape[:2], dtype="uint8") * 255
            cv2.drawContours(mask, bad_contours, -1, 0, -1)

            # Apply mask on matrix
            result = np.multiply(int_mat, mask > 0)

            # Rescale to [0,1]
            result = result / 255.

            return result

    # get_ecart_ligne
    def get_ecart_ligne(self, image):

        def poly_2_interpol(image):
            nonzeros_indexes = np.nonzero((image > self.LINE_THRESHOLD).copy())
            x = nonzeros_indexes[0]
            y = nonzeros_indexes[1]
            if len(x) < 2:
                return None, None
            else:
                poly_coeff = np.polyfit(x, y, 2)

            # Create interpolated function
            def interpol_function(x):
                values = np.int16(poly_coeff[2] + x * poly_coeff[1] + x ** 2 * poly_coeff[0])
                return np.minimum(np.maximum(values, 0), self.WIDTH - 1)

            return interpol_function, poly_coeff

        # Interpole la ligne � partir des points x, y
        poly2, poly_coeff = poly_2_interpol(image)

        if poly2 is None:
            # Si on a perdu la ligne, on fait l'hypothese qu'elle est du meme cote que la derniere fois qu'on l'a vue
            return self.position_ligne_1, self.position_ligne_2, None
        else:
            position_1 = (2.0 * poly2(self.X_INFERENCE_POINT_1) / self.WIDTH) - 1.0
            position_2 = (2.0 * poly2(self.X_INFERENCE_POINT_2) / self.WIDTH) - 1.0
            return position_1, position_2, poly_coeff
