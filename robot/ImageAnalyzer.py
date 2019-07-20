# coding=utf-8
import cv2
import numpy as np

from robot.Component import Component


class ImageAnalyzer(Component):
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

    IMAGE_CLIPPED_LENGHT = 300

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
    distance_obstacle_line = None
    side_avoidance = None

    def __init__(self, car, image_warper, show_and_wait=False):
        self.car = car
        self.image_warper = image_warper
        self.show_and_wait = show_and_wait

    def execute(self):
        mask_line, mask_obstacles = self.car.get_images()
        if mask_line is not None and mask_obstacles is not None:
            mask_line = self.clean_mask_line(mask_line)
            mask_obstacles = self.clean_mask_obstacle(mask_obstacles)
            mask_line = self.remove_line_behind_obstacles(mask_line, mask_obstacles)
            warped_line = self.image_warper.warp(mask_line)
            warped_obstacles = self.image_warper.warp(mask_obstacles)

            if self.show_and_wait:
                # Display final mask for debug
                mask_for_debug_display = np.zeros((warped_line.shape[0], warped_line.shape[1], 3))
                mask_for_debug_display[..., 1] = warped_obstacles
                mask_for_debug_display[..., 2] = warped_line
                cv2.imshow('merged final', mask_for_debug_display)
                cv2.waitKey(0)

            self.poly_1_interpol(warped_line)
            self.compute_line_horizontal_offset(warped_line)
            self.compute_obstacle_position(warped_line, warped_obstacles)

    def clean_mask_line(self, image):

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
        clipped = image[self.IMAGE_CLIPPED_LENGHT:, :]
        print(clipped.shape)
        nonzeros_indexes = np.nonzero(clipped > self.LINE_THRESHOLD)
        y = nonzeros_indexes[0]
        x = nonzeros_indexes[1]
        if len(x) < 2:
            self.poly_coeff_1 = None
        else:
            self.poly_coeff_1 = np.polyfit(y, x, 1)

    def compute_line_horizontal_offset(self, image):
        nonzeros_indexes = np.nonzero((image > self.LINE_THRESHOLD).copy())
        x = nonzeros_indexes[1]
        if len(x) == 0:
            self.pixel_offset_line = None
        else:
            self.pixel_offset_line = np.mean(x[-10:]) - 150

    def compute_obstacle_position(self, mask_line, mask_obstacles):
        self.BOTTOM_OBSTACLE_WINDOW_HEIGHT = 5
        self.LINE_WINDOW_HEIGHT_AT_OBSTACLE = 5

        obstacle_pixels_y, obstacle_pixels_x, = np.nonzero(mask_obstacles)
        line_pixels_y, line_pixels_x = np.nonzero(mask_line)
        print(line_pixels_x, line_pixels_y)

        if len(obstacle_pixels_y) == 0 or len(obstacle_pixels_x) == 0 \
                or len(line_pixels_y) == 0 or len(line_pixels_x) == 0:
            self.distance_obstacle_line = None
            return

        lowest_obstacle_y = np.max(obstacle_pixels_y)
        lowest_obstacle_pixels_x = obstacle_pixels_x[
            np.where(obstacle_pixels_y >= lowest_obstacle_y - self.BOTTOM_OBSTACLE_WINDOW_HEIGHT)]
        lowest_obstacle_pixels_y = obstacle_pixels_y[
            np.where(obstacle_pixels_y >= lowest_obstacle_y - self.BOTTOM_OBSTACLE_WINDOW_HEIGHT)]

        if len(line_pixels_x) == 0:
            self.distance_obstacle_line = None
            return

        low_left_obstacle_x = np.min(lowest_obstacle_pixels_x)
        low_left_obstacle_y = lowest_obstacle_y
        low_right_obstacle_x = np.max(lowest_obstacle_pixels_x)
        low_right_obstacle_y = lowest_obstacle_y

        # Find points on the line that are the closest to the bottom left and bottom right of the obstacle
        idx_line_closest_to_left_obstacle = np.argmin(
            np.square(low_left_obstacle_x - line_pixels_x) + np.square(low_left_obstacle_y - line_pixels_y))
        idx_line_closest_to_right_obstacle = np.argmin(
            np.square(low_right_obstacle_x - line_pixels_x) + np.square(low_right_obstacle_y - line_pixels_y))
        x_line_closest_left = line_pixels_x[idx_line_closest_to_left_obstacle]
        y_line_closest_left = line_pixels_y[idx_line_closest_to_left_obstacle]
        x_line_closest_right = line_pixels_x[idx_line_closest_to_right_obstacle]
        y_line_closest_right = line_pixels_y[idx_line_closest_to_right_obstacle]

        # Compute distances
        distance_left_obstacle = np.sqrt(
            (x_line_closest_left - low_left_obstacle_x) ** 2 + (y_line_closest_left - low_left_obstacle_y) ** 2)
        distance_right_obstacle = np.sqrt(
            (x_line_closest_right - low_right_obstacle_x) ** 2 + (y_line_closest_right - low_right_obstacle_y) ** 2)

        # Find position according to line
        position_left_obstacle = np.sign(low_left_obstacle_x - x_line_closest_left)
        position_right_obstacle = np.sign(low_right_obstacle_x - x_line_closest_right)

        # Transform distance to signed distance
        distance_left_obstacle *= position_left_obstacle
        distance_right_obstacle *= position_right_obstacle

        self.side_avoidance = 1 if (abs(distance_left_obstacle) > abs(distance_right_obstacle)) else -1
        self.distance_obstacle_line = min(distance_left_obstacle, distance_right_obstacle, key=abs)

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

    def get_distance_obstacle_line(self):
        return self.distance_obstacle_line

    def remove_line_behind_obstacles(self, mask_line, mask_obstacles):
        diff = mask_line - mask_obstacles
        return (diff == 255) * diff

    def clean_mask_obstacle(self, mask_obstacles):
        return np.clip(mask_obstacles, 0, 1) * 255
