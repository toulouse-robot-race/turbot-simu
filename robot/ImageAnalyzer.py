# coding=utf-8
import cv2
import numpy as np


def clean_mask_obstacle(mask_obstacles):
    return np.clip(mask_obstacles, 0, 1) * 255


class ImageAnalyzer:
    # Constants for cleaning inference results. IMPORTANT to recalibrate this on real conditions track.
    MIN_AREA_RATIO = 0.35  # if area / area_of_biggest_contour is less than this ratio, contour is bad
    MIN_AREA_TO_KEEP = 100.  # if max_area if less than this, reject all image
    MIN_THRESHOLD_CONTOUR = 10
    MAX_VALUE_CONTOUR = 255

    LINE_THRESHOLD = 0.10
    BOTTOM_OBSTACLE_WINDOW_HEIGHT = 5
    LINE_WINDOW_HEIGHT_AT_OBSTACLE = 5

    # Param�tres de class
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
    poly_1_coefs = None
    poly_2_coefs = None
    position_obstacle = False
    parallelism = 0
    obstacle_exists = False
    obstacle_in_brake_zone = False
    obstacle_position_unlock = True
    obstacle_position_lock = False
    pixel_offset_line = None
    distance_obstacle_line = None
    side_avoidance = None

    final_mask_for_display = None

    def __init__(self, car, image_warper, show_and_wait=False, log=True):
        self.log = log
        self.car = car
        self.image_warper = image_warper
        self.show_and_wait = show_and_wait
        self.clip_length = 0
        self.offset_baseline_height = 50

    def analyze(self):
        mask_line, mask_obstacles = self.car.get_images()
        if mask_line is not None and mask_obstacles is not None:
            mask_line = self.clean_mask_line(mask_line)
            mask_obstacles = clean_mask_obstacle(mask_obstacles)
            mask_line = self.image_warper.warp(mask_line, "line")
            mask_obstacles = self.image_warper.warp(mask_obstacles, "obstacle")
            mask_line = self.clip_image(mask_line)

            self.poly_1_interpol(mask_line)
            self.compute_robot_horizontal_offset_from_poly1()
            print("offset", self.pixel_offset_line)
            self.compute_obstacle_position(mask_line, mask_obstacles)

            if self.show_and_wait or self.log:

                # Display final mask for debug
                self.poly_2_interpol(mask_line)
                self.final_mask_for_display = np.zeros((mask_line.shape[0], mask_line.shape[1], 3))
                self.final_mask_for_display[..., 1] = mask_obstacles
                self.final_mask_for_display[..., 2] = mask_line
                self.draw_line_offset_line()
                draw_interpol_poly1(self.final_mask_for_display, self.poly_1_coefs)
                draw_interpol_poly2(self.final_mask_for_display, self.poly_2_coefs)
                if self.show_and_wait:
                    cv2.imshow('merged final', self.final_mask_for_display)
                    cv2.waitKey(0)

    def clip_image(self, image):
        image[:self.clip_length, :] = 0
        return image

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
        self.poly_1_coefs = self.poly_interpol(image, 1)

    def poly_2_interpol(self, image):
        self.poly_2_coefs = self.poly_interpol(image, 2)

    def poly_interpol(self, image, degree):
        nonzeros_indexes = np.nonzero(image > self.LINE_THRESHOLD)
        y = nonzeros_indexes[0]
        x = nonzeros_indexes[1]
        if len(x) < 2:
            return None
        else:
            return np.polyfit(y, x, degree)

    def draw_line_offset_line(self):
        lineY = (self.image_warper.warped_height - self.offset_baseline_height)
        shape = self.final_mask_for_display.shape
        lineX = np.arange(0, shape[1] - 1)
        self.final_mask_for_display[lineY, lineX, :] = 1

    def compute_robot_horizontal_offset_from_poly1(self):
        if self.poly_1_coefs is None:
            self.pixel_offset_line = None
        else:
            self.pixel_offset_line = (self.poly_1_coefs[0] * (
                    self.image_warper.warped_height - self.offset_baseline_height)
                                      + self.poly_1_coefs[1]) - (self.image_warper.warped_width / 2)

    def compute_obstacle_position(self, mask_line, mask_obstacles):

        obstacle_pixels_y, obstacle_pixels_x, = np.nonzero(mask_obstacles)
        line_pixels_y, line_pixels_x = np.nonzero(mask_line)

        if len(obstacle_pixels_y) == 0 or len(obstacle_pixels_x) == 0 \
                or len(line_pixels_y) == 0 or len(line_pixels_x) == 0:
            self.distance_obstacle_line = None
            return

        lowest_obstacle_y = np.max(obstacle_pixels_y)
        lowest_obstacle_pixels_x = obstacle_pixels_x[
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

    def set_clip_length(self, clip_length):
        if clip_length < 0 or clip_length > self.image_warper.warped_height:
            raise Exception("Clip lenght out of final image bounds")
        self.clip_length = clip_length

    def set_offset_baseline_height(self, offset_line_height):
        if offset_line_height < 0 or offset_line_height > self.image_warper.warped_height:
            raise Exception("Clip lenght out of final image bounds")
        self.offset_baseline_height = offset_line_height


def draw_interpol_poly1(image, poly_coefs):
    def poly1(x):
        return poly_coefs[0] * x + poly_coefs[1]

    return draw_interpol(image, poly1)


def draw_interpol_poly2(image, poly_coefs):
    def poly2(x):
        return poly_coefs[0] * x * x + poly_coefs[1] * x + poly_coefs[2]
    return draw_interpol(image, poly2)


def draw_interpol(image, interpol_function):
    shape = image.shape
    xall = np.arange(0, shape[0] - 1)
    ypoly = interpol_function(xall).astype(int)
    ypoly = np.clip(ypoly, 0, shape[1] - 2)
    image[xall, ypoly, :] = 0
    image[xall, ypoly, 1] = 255
    return image
