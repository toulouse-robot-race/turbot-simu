import numpy as np

from robot.Component import Component


class Camera(Component):
    MASK_LINE_FILE = "mask_line"

    MASK_OBSTACLE_FILE = "mask_line"

    mask_line = None
    mask_obstacles = None

    def execute(self):
        # Consume masks produced by inference process
        mask_line = np.load(self.MASK_LINE_FILE)
        mask_obstacles = np.load(self.MASK_OBSTACLE_FILE)
