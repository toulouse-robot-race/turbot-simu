# coding=utf-8
import cv2
import numpy as np

from robot.Config import CAMERA_DELAY


class ImageAnalyzer:
    # Constantes
    MODEL_FILENAME = 'deep_learning_models/craie_quarter_filters_6.h5'
    DELAY_EXECUTION = 0.07
    LINE_THRESHOLD = 0.10
    EVITEMENT_OFFSET = 0.30
    X_INFERENCE_POINT_1 = 100  # Point depuis le haut de l'image pris pour calculer l'ecart par rapport a la ligne
    X_INFERENCE_POINT_2 = 150  # Point depuis le haut de l'image pris pour calculer l'ecart par rapport a la ligne
    WIDTH = 320
    HEIGHT = 240
    SAVE_TO_FILENAME = "/tmp_ram/imageAnalysisResult.json"
    LOG_EVERY_N_IMAGES = 20  # Loggue les images toutes les N
    LOG_BUFFER_SIZE = 10  # Taille du buffer (nombre d'images enregistrees dans un fichier)

    # Constants for cleaning inference results. IMPORTANT to recalibrate this on real conditions track.
    MIN_AREA_RATIO = 0.35  # if area / area_of_biggest_contour is less than this ratio, contour is bad
    MIN_AREA_TO_KEEP = 100.  # if max_area if less than this, reject all image
    MIN_THRESHOLD_CONTOUR = 10
    MAX_VALUE_CONTOUR = 255

    # Constants for obstacle detection
    MIN_X_TO_CONSIDER_OBSTACLE_EXISTS = 45  # If obstacle is low enough in image, consider it as existing
    MIN_X_TO_COMPUTE_OBSTACLE_SIDE_ETROIT = 45  # If obstacle is low enough in image, we can compute its side (only between Y_SIDE_GAUCHE and Y_SIDE_DROITE)
    MIN_X_TO_COMPUTE_OBSTACLE_SIDE_LARGE = 90  # If obstacle is low enough in image, we can compute its side (all width)
    Y_SIDE_GAUCHE = 110  # Left border of "etroit zone" (for computing obstacle side etroit)
    Y_SIDE_DROITE = WIDTH - Y_SIDE_GAUCHE  # Right border of "etroit zone"
    MIN_X_TO_LOCK_OBSTACLE_POSITION = 100  # If obstacle passes this X, we lock its position
    MAX_X_TO_UNLOCK_OBSTACLE_POSITION = 106  # If no obstacles below this X, we can unlock position
    MIN_X_BRAKE = 130  # If obstacle gets into this zone, stop the car (X of the trapeze)
    MAX_X_BRAKE = 220  # Don't compute brake zone below this zone
    MIN_Y_BRAKE = 90  # Grande base du trapeze (gauche). La grande base est prise au bas de l'image
    MAX_Y_BRAKE = 228  # Grande base du trapeze (droite)
    MIN_Y_BRAKE_AT_MIN_X = 130  # Petite base du trapeze (gauche)
    MAX_Y_BRAKE_AT_MIN_X = 190  # Petite base du trapeze (droite)
    MIN_PIXELS_OBSTACLE_BRAKE = 5
    # Constant for computing parallelism
    MIDDLE_HORIZON_X = -25  # Hauteur de l'horizon (negatif = au-dessus de l'image)

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
    poly_coeff_1 = None
    poly_coeff_const = None
    position_obstacle = False
    parallelism = 0
    obstacle_exists = False
    obstacle_in_brake_zone = False
    obstacle_position_unlock = True
    obstacle_position_lock = False
    pixel_offset_line = None

    def __init__(self, simulator, line_cam_handle, obstacles_cam_handle, image_warper):
        self.obstacles_cam_handle = obstacles_cam_handle
        self.line_cam_handle = line_cam_handle
        self.image_warper = image_warper
        self.line_cam_handle = line_cam_handle
        self.simulator = simulator

    def execute(self):
        resolution, byte_array_image_string = self.simulator.get_gray_image(self.line_cam_handle, CAMERA_DELAY)
        resolution_obstacles, byte_array_image_string_obstacle = self.simulator.get_gray_image(
            self.obstacles_cam_handle, CAMERA_DELAY)

        if resolution is not None and byte_array_image_string is not None:
            mask0 = self.convert_image_to_numpy(byte_array_image_string, resolution)
            mask0 = self.clean_mask(mask0)
            warped = self.image_warper.warp(mask0)
            self.poly_1_interpol(warped)
            self.compute_line_horizontal_offset(warped)

            # if resolution_obstacles is not None and byte_array_image_string_obstacle is not None:
            #     mask1 = self.convert_image_to_numpy(byte_array_image_string_obstacle, resolution_obstacles)
            #     mask1 = self.image_warper.warp(mask1, True)
            #     self.obstacle_exists, self.position_obstacle, self.obstacle_position_lock, \
            #     self.obstacle_position_unlock, self.obstacle_in_brake_zone = self.findObstacles(
            #         mask1, poly2)

    def convert_image_to_numpy(self, byte_array_image_string, resolution):
        return np.flipud(np.fromstring(byte_array_image_string, dtype=np.uint8).reshape(resolution[::-1]))

    def clean_mask(self, image):

        # Scale to openCV format: transform [0.,1.] to [0,255]
        int_mat = (image * 255).astype(np.uint8)

        # Get contours
        _, thresh = cv2.threshold(int_mat, self.MIN_THRESHOLD_CONTOUR, self.MAX_VALUE_CONTOUR, 0)
        result = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Open cv version compatibility issue
        if len(result) == 2:
            contours = result[0]
        else:
            contours = result[1]
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

    def poly_1_interpol(self, image):
        nonzeros_indexes = np.nonzero((image > self.LINE_THRESHOLD).copy())
        x = nonzeros_indexes[0]
        y = nonzeros_indexes[1]
        if len(x) < 2:
            self.poly_coeff_1 = None
        else:
            self.poly_coeff_1 = np.polyfit(x, y, 1)

    def compute_line_horizontal_offset(self, image):
        nonzeros_indexes = np.nonzero((image > self.LINE_THRESHOLD).copy())
        x = nonzeros_indexes[0]
        y = nonzeros_indexes[1]
        if len(x) == 0:
            self.pixel_offset_line = None
        else:
            self.pixel_offset_line = y[-1] - 150

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
            return self.position_ligne_1, self.position_ligne_2, None, None, None
        else:
            # Calcule la position des points proches et lointains
            y_inference_1 = poly2(self.X_INFERENCE_POINT_1)
            y_inference_2 = poly2(self.X_INFERENCE_POINT_2)
            position_1 = (2.0 * y_inference_1 / self.WIDTH) - 1.0
            position_2 = (2.0 * y_inference_2 / self.WIDTH) - 1.0

            # Calcule le parallelisme par rapport a la ligne de fuite
            middle_horizon_y = int(self.WIDTH / 2)
            middle_horizon = np.array([self.MIDDLE_HORIZON_X, middle_horizon_y])
            point_proche = np.array([self.X_INFERENCE_POINT_2, y_inference_2])
            point_lointain = np.array([self.X_INFERENCE_POINT_1, y_inference_1])
            vecteur_ligne_de_fuite = middle_horizon - point_proche
            vecteur_ligne_blanche = point_lointain - point_proche
            # Calcule le produit vectoriel P1P2 x ligne_de_fuite
            parallelism = np.cross(vecteur_ligne_blanche, vecteur_ligne_de_fuite) / (
                    np.linalg.norm(vecteur_ligne_de_fuite) * np.linalg.norm(vecteur_ligne_blanche))

            return position_1, position_2, poly_coeff, poly2, parallelism

    def create_trapezoidal_matrix(self):
        print("Create trapezoidal matrix for obstacle detection")
        matrix_height = self.HEIGHT - self.MIN_X_BRAKE
        trapeze_height = self.MAX_X_BRAKE - self.MIN_X_BRAKE
        trapezoidal_matrix_brake_zone = np.zeros((matrix_height, self.WIDTH))
        for i in range(trapeze_height):
            left_index = int(
                (self.MIN_Y_BRAKE - self.MIN_Y_BRAKE_AT_MIN_X) * i / trapeze_height + self.MIN_Y_BRAKE_AT_MIN_X)
            right_index = int(
                (self.MAX_Y_BRAKE - self.MAX_Y_BRAKE_AT_MIN_X) * i / trapeze_height + self.MAX_Y_BRAKE_AT_MIN_X)
            trapezoidal_matrix_brake_zone[i, left_index:right_index] = 1
        # Convert to boolean
        trapezoidal_matrix_brake_zone = trapezoidal_matrix_brake_zone != 0
        return trapezoidal_matrix_brake_zone

    # Find obstacles in image and localize them (left or right of image)
    # Returns: obstacle_exists (boolean), side_of_obstacle (-1 for left, 1 for right, 0 otherwise)
    def findObstacles(self, image, poly2):

        # Scale to openCV format: transform [0.,1.] to [0,255]
        intMat = (image * 255).astype(np.uint8)

        # Get contours
        _, thresh = cv2.threshold(intMat, self.MIN_THRESHOLD_CONTOUR, self.MAX_VALUE_CONTOUR, 0)
        result = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # Open cv version compatibility issue
        if len(result) == 2:
            contours = result[0]
        else:
            contours = result[1]

        if len(contours) == 0:
            # No obstacle detected
            return False, 0, False, True, False
        else:
            # Compute features of contours
            cnt_processed = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                # Keep only biggest contours
                if area > self.MIN_AREA_TO_KEEP:
                    # Compute bounding rectangle
                    x, y, w, h = cv2.boundingRect(cnt)
                    # Compute middle of obstacle basis
                    cy = int(x + w / 2)
                    cx = int(y + h)
                    # Append contour in list
                    cnt_processed.append({'cnt': cnt, 'cx': cx, 'cy': cy, 'area': area})

        # Check if obstacle gets into the different zones of interest
        obstacle_exists = False
        obstacle_position_lock = False
        obstacle_position_unlock = True
        for cntp in cnt_processed:
            if cntp['cx'] > self.MIN_X_TO_CONSIDER_OBSTACLE_EXISTS:
                obstacle_exists = True
            if cntp['cx'] > self.MIN_X_TO_LOCK_OBSTACLE_POSITION:
                obstacle_position_lock = True
            if cntp['cx'] > self.MAX_X_TO_UNLOCK_OBSTACLE_POSITION:
                obstacle_position_unlock = False

        # Check if obstacle gets into brake zone
        all_processed_contours = [cntp['cnt'] for cntp in cnt_processed]
        mask_contours = np.zeros(image.shape[:2], dtype="uint8")
        cv2.drawContours(mask_contours, all_processed_contours, -1, 255, -1)
        # Crop to brake zone on X axis
        mask_contours_brake_zone = mask_contours[self.MIN_X_BRAKE:, :]
        # Check if there is obstacle in brake zone by comparing with trapezoidal matrix
        obstacle_in_brake_zone = True if np.count_nonzero(np.logical_and(mask_contours_brake_zone,
                                                                         self.create_trapezoidal_matrix())) >= self.MIN_PIXELS_OBSTACLE_BRAKE else False

        # Check side of closest obstacle
        side_of_closest_obstacle = 0
        if poly2 is not None and len(cnt_processed) > 0:
            # Find closest obstacle
            closest_obstacle = None
            for cntp in cnt_processed:
                cx = cntp['cx']
                # Check if obstacle is low enough on image. If it is too high, difficult to see its side
                if cx > self.MIN_X_TO_COMPUTE_OBSTACLE_SIDE_LARGE or (
                        cx > self.MIN_X_TO_COMPUTE_OBSTACLE_SIDE_ETROIT and self.Y_SIDE_GAUCHE < cx < self.Y_SIDE_DROITE):
                    # Check if it is the closest obstacle
                    if closest_obstacle is None:
                        closest_obstacle = cntp
                    else:
                        if closest_obstacle['cx'] < cntp['cx']:
                            closest_obstacle = cntp
            # If there is a closest obstacle, find its side
            if closest_obstacle is not None:
                # Compute position of line at obstacle level
                yline = poly2(closest_obstacle['cx'])
                # Check position of obstacle compared to position of line
                if yline < closest_obstacle['cy']:
                    side_of_closest_obstacle = 1
                else:
                    side_of_closest_obstacle = -1

        return obstacle_exists, side_of_closest_obstacle, obstacle_position_lock, \
               obstacle_position_unlock, obstacle_in_brake_zone

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
        return self.poly_coeff_1

    def getPolyCoeffConst(self):
        return self.poly_coeff_const

    def getObstacleExists(self):
        return self.obstacle_exists

    def getPositionObstacle(self):
        return self.position_obstacle

    def getParallelism(self):
        return self.parallelism

    def getObstacleInBrakeZone(self):
        return self.obstacle_in_brake_zone

    def getStartDetected(self):
        pass

    def unlockObstacle(self):
        self.position_obstacle = 0

    def get_line_offset(self):
        return self.pixel_offset_line
