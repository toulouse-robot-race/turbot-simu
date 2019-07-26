from robot.Component import Component


class SpeedController(Component):
    def __init__(self, simulator, motor_handles, simulation_step_time):
        self.simulation_step_time = simulation_step_time
        self.motor_handles = motor_handles
        self.max_speed = 100000 * 0.11 / 60  # In duty cycle mode, this could go up to 95000 (95%), or even a little more, close to 100%
        self.min_speed = 7000 * 0.11 / 60
        self.simulator = simulator
        self.previous_speed = 0
        self.speed = 0
        self.min_speed = 0
        self.max_acceleration_step = 15000  # Max acceleration in speed unit per seconds
        self.min_acceleration_step = 0
        self.max_deceleration_step = 15000  # Max deceleration in speed unit per seconds
        self.min_deceleration_step = 0
        self.acceleration_step = self.max_acceleration_step
        self.deceleration_step = self.max_deceleration_step
        self.speed_target = 0
        self.simulation_step_time = self.simulator.get_simulation_time_step()

    def set_speed_target(self, speed_target):
        self.speed_target = speed_target

    def set_speed_percent(self, speed_percent):
        if not 0 <= speed_percent <= 100:
            raise Exception("speed percent must be beetwent 0 and 100, was %f" % speed_percent)
        self.speed_target = (speed_percent / 100) * self.max_speed
        if self.speed_target < self.min_speed:
            self.speed_target = 0
        print("target speed is now %d" % self.speed_target)

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
        angular_speed = -self.speed
        self.simulator.set_target_speed(self.motor_handles[0], angular_speed)
        self.simulator.set_target_speed(self.motor_handles[1], angular_speed)
