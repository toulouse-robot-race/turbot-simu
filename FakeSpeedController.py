import numpy as np

from Config import SPEED_COEF, TACHO_COEF


class SpeedController:
    def __init__(self, simulator, motor_handles, simulation_step_time, base_car):
        self.base_car = base_car
        self.simulation_step_time = simulation_step_time
        self.motor_handles = motor_handles
        self.simulator = simulator
        self.previous_speed = 0
        self.tacho = 0
        self.previous_pos = np.array([0, 0, 0])
        self.speed = 0
        self.min_speed = 0
        self.deceleration_step = 2  # TODO make this dependent on time step (on real Turbodroid it is 0.1)
        self.acceleration_step = 2  # TODO make this dependent on time step
        self.speed_target = 0
        self.simulation_step_time = self.simulator.get_simulation_time_step()

    def set_speed_target(self, speed_target):
        self.speed_target = speed_target

    def execute(self):
        self.update_speed()
        self.compute_tacho()
        self.send_speed_command()

    def update_speed(self):
        # Compute time elapsed since last update
        # Update execution time
        # Compute new speed
        if (self.speed_target - self.deceleration_step) <= self.speed <= (self.speed_target + self.acceleration_step):
            # If we are close to speed_target, set speed to speed_target
            self.speed = self.speed_target
        elif self.speed < self.speed_target:
            # If we must accelerate
            self.speed += self.acceleration_step
            # If we have not reached min_speed, set to min_speed
            if self.speed < self.min_speed:
                self.speed = self.min_speed
        elif self.speed > self.speed_target:
            # If we must decelerate
            self.speed -= self.deceleration_step
            # If we have already decelerated to min_speed, set speed to zero
            if self.speed < self.min_speed:
                self.speed = 0
        # Send command to VESC
        self.send_speed_command()

    def send_speed_command(self):
        angular_speed = self.speed * SPEED_COEF
        self.simulator.set_target_speed(self.motor_handles[0], angular_speed)
        self.simulator.set_target_speed(self.motor_handles[1], angular_speed)

    def get_tacho(self):
        return self.tacho

    def compute_position_vector(self):
        current_pos = self.simulator.get_object_position(self.base_car)
        current_pos = current_pos if current_pos is not None else [0, 0, 0]
        position_vector = np.array(current_pos) - np.array(self.previous_pos)
        self.previous_pos = current_pos
        return position_vector

    def compute_tacho(self):
        position_vector = self.compute_position_vector()
        self.tacho += np.linalg.norm(position_vector) * TACHO_COEF
