import time

from robot.Component import Component
from robot.real.Vesc import Vesc


class SpeedController(Component):
    def __init__(self, vesc, enable=True):
        self.vesc = vesc
        self.enabled = enable
        if not enable:
            print("SPEED CONTROLLER NOT ENABLED, TEST MODE")
        self.max_speed = 50000  # In duty cycle mode, this could go up to 95000 (95%), or even a little more,
        # close to 100%
        self.min_speed = 7000
        self.DELAY_BETWEEN_EXECUTIONS = 0.05  # Delay in seconds between two executions of speed update
        self.BRAKE_CURRENT = 15000  # Break current in mA
        self.REVERSE_SPEED = 10000
        self.speed = 0
        self.speed_target = 0
        self.max_acceleration_step = 15000  # Max acceleration in speed unit per seconds
        self.min_acceleration_step = 0
        self.max_deceleration_step = 15000  # Max deceleration in speed unit per seconds
        self.min_deceleration_step = 0
        self.acceleration_step = self.max_acceleration_step
        self.deceleration_step = self.max_deceleration_step
        self.last_execution_time = None
        self.tachometer = None
        self.rpm = 0

    def set_speed_percent(self, speed_percent):
        if not 0 <= speed_percent <= 100:
            raise Exception("speed percent must be beetwent 0 and 100, was %f" % speed_percent)
        self.speed_target = (speed_percent / 100) * self.max_speed
        if self.speed_target < self.min_speed:
            self.speed_target = 0
        print("target speed is now %d" % self.speed_target)

    # Make a reverse at a fixed speed
    def set_reverse(self):
        self.speed = -self.REVERSE_SPEED
        self.send_speed_command()

    def set_acceleration_percent(self, acceleration_percent):
        if not 0 <= acceleration_percent <= 100:
            raise Exception("acceleration percent must be beetwent 0 and 100, was %f" % acceleration_percent)
        self.acceleration_step = (acceleration_percent / float(100)) * (
                self.max_acceleration_step - self.min_acceleration_step) + self.min_acceleration_step
        print("acceleration is now %d" % self.acceleration_step)

    def set_deceleration_percent(self, deceleration_percent):
        if not 0 <= deceleration_percent <= 100:
            raise Exception("deceleration percent must be beetwent 0 and 100, was %f" % deceleration_percent)
        self.deceleration_step = (deceleration_percent / float(100)) * (
                self.max_deceleration_step - self.min_deceleration_step) + self.min_deceleration_step
        print("deceleration is now %d" % self.deceleration_step)

    # Method execute must be called on a regular basis
    def execute(self):
        if not self.enabled:
            return
        self.update_speed()

    def update_speed(self):
        # Compute time elapsed since last update
        delta_t = time.time() - self.last_execution_time if self.last_execution_time is not None else 1
        # Update execution time
        self.last_execution_time = time.time()

        if self.speed < self.speed_target:
            # If we must accelerate
            self.speed += self.acceleration_step * delta_t

            if self.speed > self.speed_target:
                self.speed = self.speed_target

        elif self.speed > self.speed_target:
            # If we must decelerate
            self.speed -= self.deceleration_step * delta_t

            if self.speed < self.speed_target:
                self.speed = self.speed_target

        # Send command to VESC
        self.send_speed_command()

    def send_speed_command(self):
        self.vesc.send_speed_command(self.speed)


if __name__ == '__main__':
    vesc = Vesc()
    speedController = SpeedController(vesc)
    speedController.set_speed_percent(60)
    for i in range(3):
        speedController.execute()
        time.sleep(1)
    speedController.set_speed_percent(20)
    for i in range(3):
        speedController.execute()
        time.sleep(1)
    time.sleep(5)
