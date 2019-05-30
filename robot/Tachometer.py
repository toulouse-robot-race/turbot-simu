import numpy as np

from robot.Config import TACHO_COEF


class Tachometer:

    def __init__(self, simulator, base_car):
        self.delta_tacho = 0
        self.simulator = simulator
        self.base_car = base_car
        self.tacho = 0
        self.previous_pos = None

    def execute(self):
        self.compute_tacho()

    def compute_tacho(self):
        current_pos = self.simulator.get_object_position(self.base_car)
        orientation = self.simulator.get_object_orientation(self.base_car)

        if current_pos is None or orientation is None:
            return

        if self.previous_pos is None:
            self.previous_pos = current_pos
            return

        position_vector = np.array(current_pos) - np.array(self.previous_pos)
        self.previous_pos = current_pos
        gyro_vector = np.array([np.sin(orientation[2]), -np.cos(orientation[2]), 0])
        self.delta_tacho = position_vector.dot(gyro_vector) * TACHO_COEF
        self.tacho += self.delta_tacho

    def get_tacho(self):
        return self.tacho

    def get_delta_tacho(self):
        return self.delta_tacho

    def reset(self):
        self.tacho = 0
        self.delta_tacho = 0
        self.previous_pos = None
