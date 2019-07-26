import time

import pyvesc
import serial

from robot.Component import Component


class SpeedController(Component):
    def __init__(self, enable=True):
        self.enabled = enable
        if not enable:
            print("SPEED CONTROLLER NOT ENABLED, TEST MODE")
        # TODO find real max and min values
        self.max_speed = 50000  # In duty cycle mode, this could go up to 95000 (95%), or even a little more, close to 100%
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
        if enable:
            self.serial = serial.Serial('/dev/ttyACM0', baudrate=115200, timeout=0.05)
        self.last_execution_time = 0.
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

        # If it is time to update
        if (time.time() - self.last_execution_time) > self.DELAY_BETWEEN_EXECUTIONS:

            # Update speed
            self.update_speed()

            # Request data from VESC
            self.serial.write(pyvesc.encode_request(pyvesc.GetValues))

            # Check if new data has been received from VESC
            if self.serial.in_waiting > 61:
                (response, consumed) = pyvesc.decode(self.serial.read(61))
                # print ("Consumed", consumed, "Serial response: ", response)
                if response is not None:
                    for sensor, value in response.__dict__.items():
                        if sensor == 'tachometer':
                            print("tachometer: ", value)
                            self.tachometer = value
                        if sensor == 'rpm':
                            print("rpm: ", value)
                            self.rpm = value
                        if sensor == 'temp_mos1':
                            print("temp mos1: ", value)
                        if sensor == 'v_in':
                            print("v_in: ", value)

    def update_speed(self):
        # Compute time elapsed since last update
        delta_t = time.time() - self.last_execution_time
        # Update execution time
        self.last_execution_time = time.time()
        # Compute new speed
        if (self.speed_target - self.deceleration_step) <= self.speed <= (self.speed_target + self.acceleration_step):
            # If we are close to speed_target, set speed to speed_target
            self.speed = self.speed_target
        elif self.speed < self.speed_target:
            # If we must accelerate
            self.speed += self.acceleration_step * delta_t
            # If we have not reached min_speed, set to min_speed
            if self.speed < self.min_speed:
                self.speed = self.min_speed
        elif self.speed > self.speed_target:
            # If we must decelerate
            self.speed -= self.deceleration_step * delta_t
            # If we have already decelerated to min_speed, set speed to zero
            if self.speed < self.min_speed:
                self.speed = 0
        # Send command to VESC
        self.send_speed_command()

    # Send speed command to VESC
    def send_speed_command(self):
        print("Sending to VESC. Duty Cycle : %s" % self.speed)
        # noinspection PyArgumentList
        msg = pyvesc.SetDutyCycle(int(self.speed))
        packet = pyvesc.encode(msg)
        if self.enabled:
            self.serial.write(packet)

    # Send brake commande to VESC
    def send_brake_command(self):
        # noinspection PyArgumentList
        msg = pyvesc.SetCurrentBrake(self.BRAKE_CURRENT)
        packet = pyvesc.encode(msg)
        if self.enabled:
            self.serial.write(packet)

    def get_tacho(self):
        return self.tachometer
