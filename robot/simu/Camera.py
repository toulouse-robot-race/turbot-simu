import numpy as np

from robot.Component import Component
from robot.simu.Config import CAMERA_DELAY


class Camera(Component):

    def __init__(self, simulator, line_cam_handle, obstacles_cam_handle):
        self.line_cam_handle = line_cam_handle
        self.obstacles_cam_handle = obstacles_cam_handle
        self.simulator = simulator

    mask_line = None

    mask_obstacles = None

    def execute(self):
        resolution, byte_array_image_string = self.simulator.get_gray_image(self.line_cam_handle, CAMERA_DELAY)
        resolution_obstacles, byte_array_image_string_obstacle = self.simulator.get_gray_image(
            self.obstacles_cam_handle, CAMERA_DELAY)

        if resolution is not None and byte_array_image_string is not None \
                and resolution_obstacles is not None and byte_array_image_string_obstacle is not None:
            mask_line = convert_image_to_numpy(byte_array_image_string, resolution)
            self.mask_obstacles = convert_image_to_numpy(byte_array_image_string_obstacle, resolution_obstacles)
            self.mask_line = remove_line_behind_obstacles(mask_line, self.mask_obstacles)


def remove_line_behind_obstacles(mask_line, mask_obstacles):
    np.clip(mask_obstacles, 0, 1) * 255
    diff = mask_line - mask_obstacles
    return (diff == 255) * diff


def convert_image_to_numpy(byte_array_image_string, resolution):
    return np.flipud(np.fromstring(byte_array_image_string, dtype=np.uint8).reshape(resolution[::-1]))
