class SpeedController:
    def __init__(self, simulator, motor_handles, wheel_radius, simulation_step_time):
        self.simulation_step_time = simulation_step_time
        self.motor_handles = motor_handles
        self.simulator = simulator
        self.wheel_radius = wheel_radius
        self.previous_speed = 0
        self.tacho = 0
        self.speed = 0
        self.min_speed = 0
        self.deceleration_step = 0.1
        self.acceleration_step = 0.1
        self.speed_target = 0
        self.simulation_step_time = self.simulator.get_simulation_time_step()

    def set_speed_target(self, speed_target):
        self.speed_target = speed_target

    def execute(self):
        self.update_speed()
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
        angular_speed = -self.speed / self.wheel_radius
        self.simulator.set_target_speed(self.motor_handles[0], angular_speed)
        self.simulator.set_target_speed(self.motor_handles[1], angular_speed)

    def get_tacho(self):
        return self.tacho

    def compute_tacho(self):
        current_speed_rad_s = -self.simulator.get_joint_angular_speed(self.motor_handles[0])
        current_speed = current_speed_rad_s * self.wheel_radius
        step_distance = ((current_speed + self.previous_speed) / 2) * self.simulation_step_time
        self.tacho += step_distance
        self.previous_speed = current_speed
