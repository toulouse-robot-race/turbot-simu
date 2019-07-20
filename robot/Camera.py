import numpy as np

from robot.Config import CAMERA_DELAY


class Camera:

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
            self.mask_line = convert_image_to_numpy(byte_array_image_string, resolution)
            self.mask_obstacles = convert_image_to_numpy(byte_array_image_string_obstacle, resolution_obstacles)


def convert_image_to_numpy(byte_array_image_string, resolution):
    return np.flipud(np.fromstring(byte_array_image_string, dtype=np.uint8).reshape(resolution[::-1]))
