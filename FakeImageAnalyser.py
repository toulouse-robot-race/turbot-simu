# coding=utf-8
import numpy as np
from matplotlib import pyplot as plt
import cv2


class ImageAnalyser:
    # Constantes
    MODEL_FILENAME = 'deep_learning_models/craie_quarter_filters_6.h5'
    DELAY_EXECUTION = 0.07
    LINE_THRESHOLD = 0.10
    EVITEMENT_OFFSET = 0.30
    X_INFERENCE_POINT_1 = 100  # Point depuis le haut de l'image pris pour calculer l'ecart par rapport a la ligne
    X_INFERENCE_POINT_2 = 150  # Point depuis le haut de l'image pris pour calculer l'ecart par rapport a la ligne
    WIDTH = 320
    SAVE_TO_FILENAME = "/tmp_ram/imageAnalysisResult.json"
    LOG_EVERY_N_IMAGES = 20  # Loggue les images toutes les N
    LOG_BUFFER_SIZE = 10  # Taille du buffer (nombre d'images enregistrees dans un fichier)

    # Constants for cleaning inference results. IMPORTANT to recalibrate this on real conditions track.
    MIN_AREA_RATIO = 0.35  # if area / area_of_biggest_contour is less than this ratio, contour is bad
    MIN_AREA_TO_KEEP = 100.  # if max_area if less than this, reject all image
    MIN_THRESHOLD_CONTOUR = 10
    MAX_VALUE_CONTOUR = 255

    # Param�tres de classe
    position_consigne = 0.0
    logTimestampMemory = None
    logImageMemory = None
    logMask0Memory = None
    logMask1Memory = None
    log_counter = 0
    new_image_arrived = True

    # Param�tres pour mesurer les temps d'ex�cution
    time_start = 0.
    max_time = 0.
    first_time = True
    last_execution_time = 0

    # Initialisation de la position de la ligne (evite crash si pas de ligne detectee au lancement)
    position_ligne_1 = 0.
    position_ligne_2 = 0.
    poly_coeff_square = None

    def __init__(self, simulator, cam_handle):
        self.cam_handle = cam_handle
        self.simulator = simulator

    def execute(self):
        resolution, byte_array_image_string = self.simulator.get_gray_image(self.cam_handle)
        mask0 = self.convert_image_to_numpy(byte_array_image_string, resolution)
        mask0 = self.clean_mask(mask0)
        self.position_ligne_1, self.position_ligne_2, poly_coeff = self.get_ecart_ligne(mask0)
        if poly_coeff is not None:
            self.poly_coeff_square = poly_coeff[0]
        else:
            self.poly_coeff_square = None

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

    def getPositionLigne1(self):
        return self.position_ligne_1

    def getPositionLigne2(self):
        return self.position_ligne_2

    def getPolyCoeffSquare(self):
        return self.poly_coeff_square

    # Tells if a new image has arrived
    def isThereANewImage(self):
        return True

    def getPolyCoeff1(self):
        pass

    def getPolyCoeffConst(self):
        pass

    def getObstacleExists(self):
        pass

    def getPositionObstacle(self):
        return 0

    def getParallelism(self):
        return 0

    def getObstacleInBrakeZone(self):
        return False

    def getStartDetected(self):
        pass

    def unlockObstacle(self):
        pass

        # Tells if a new image has arrived

    def isThereANewImage(self):
        return True