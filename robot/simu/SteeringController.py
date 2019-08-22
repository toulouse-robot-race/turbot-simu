import numpy as np

from robot.Component import Component
from robot.simu.Config import STEERING_COEF


class SteeringController(Component):

    def __init__(self, simulator, steering_handles):
        self.simulator = simulator
        self.steering_handles = steering_handles

    steering = 0

    def set_steering(self, steering):
        if not -100 < steering < 100:
            raise Exception("steering must be between -100 and 100, was ", steering)
        self.steering = steering

    def execute(self):
        if -10 < self.steering < 10:
            steering_radians_pos = STEERING_COEF * (self.steering * 0.25)
        else:
            steering_radians_pos = STEERING_COEF * (self.steering * 0.155 + np.sign(self.steering) * 0.95)

        # pos_steering = steering_percent * STEERING_COEF
        self.simulator.set_target_pos(self.steering_handles[0], steering_radians_pos)
        self.simulator.set_target_pos(self.steering_handles[1], steering_radians_pos)
