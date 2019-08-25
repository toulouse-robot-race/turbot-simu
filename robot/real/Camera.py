import string

import numpy as np

from robot.Component import Component


class Camera(Component):

    def __init__(self, mask_line_file_path: string, mask_obstacle_file_path: string):
        self.mask_obstacle_file_path = mask_obstacle_file_path
        self.mask_line_file_path = mask_line_file_path


    mask_line = None

    mask_obstacles = None

    def execute(self):
        # Consume masks produced by inference process
        self.mask_line = np.load(self.mask_line_file_path).astype(float)
        self.mask_obstacles = np.load(self.mask_obstacle_file_path).astype(float)

