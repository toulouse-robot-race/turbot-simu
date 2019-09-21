import numpy as np

from robot.strategy.Strategy import Strategy

WIDTH_HALF_CORRIDOR = 50
# Offset to take into account the width of the robot when avoiding obstacles
ROBOT_WIDTH_AVOIDANCE = 40
# Quand l'obstacle est sur la ligne, on s'ecarte un peu plus, avec une marge supplémentaire
COEFF_AVOIDANCE_SAME_SIDE = 1.5
# Quand l'obstacle n'est pas sur la ligne, on s'ecarte un peu moins que la largeur qui separe l'obstacle de la ligne
COEFF_AVOIDANCE_OTHER_SIDE = 0.5


def should_compute_obstacle_offset(distance_obstacle_line):
    return distance_obstacle_line is None or abs(distance_obstacle_line) > WIDTH_HALF_CORRIDOR


class LineAngleOffset(Strategy):

    def __init__(self, image_analyzer, additional_offset, coef_angle=60, coef_offset=0.2, coef_cumul_offset=0.01):
        self.coef_offset = coef_offset
        self.coef_angle = coef_angle
        self.additional_offset = additional_offset
        self.image_analyzer = image_analyzer
        self.cumul_offset = 0
        self.coef_cumul_offset = coef_cumul_offset

    def compute_steering(self):
        self.image_analyzer.analyze()
        coeff_poly_1_line = self.image_analyzer.poly_coeff_1
        distance_obstacle_line = self.image_analyzer.distance_obstacle_line

        obstacle_avoidance_additional_offset = 0 \
            if should_compute_obstacle_offset(distance_obstacle_line) \
            else self.compute_obstacle_offset(distance_obstacle_line)

        line_offset = self.image_analyzer.pixel_offset_line

        if line_offset is None:
            line_offset = 0

        error_offset = line_offset + obstacle_avoidance_additional_offset * 3 + self.additional_offset

        self.cumul_offset = self.cumul_offset * 0.9
        self.cumul_offset += error_offset
        np.clip(self.cumul_offset,-1000,1000)

        if coeff_poly_1_line is not None and line_offset is not None:
            angle_line = -np.arctan(coeff_poly_1_line[0])
            return self.coef_angle * angle_line + self.coef_offset * error_offset + self.cumul_offset * self.coef_cumul_offset
        else:
            return None

    def compute_obstacle_offset(self, distance_obstacle_line):
        side_avoidance = self.image_analyzer.side_avoidance

        coeff_avoidance = COEFF_AVOIDANCE_SAME_SIDE \
            if (np.sign(distance_obstacle_line) == np.sign(side_avoidance)) \
            else COEFF_AVOIDANCE_OTHER_SIDE

        return (coeff_avoidance * distance_obstacle_line) + (ROBOT_WIDTH_AVOIDANCE * side_avoidance)
