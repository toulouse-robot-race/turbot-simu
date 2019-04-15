import math
import random

from Config import STEERING_COEF


class Car:

    def __init__(self, simulator, steering_handles, motors_handles, speed_controller, tachometer, gyro):
        self.gyro = gyro
        self.tachometer = tachometer
        self.motors_handles = motors_handles
        self.steering_handles = steering_handles
        self.simulator = simulator
        self.speedController = speed_controller

    def tourne(self, steering_percent):
        pos_steering = steering_percent * STEERING_COEF
        self.simulator.set_target_pos(self.steering_handles[0], pos_steering)
        self.simulator.set_target_pos(self.steering_handles[1], pos_steering)

    def avance(self, speed):
        self.speedController.set_speed_target(speed)

    def get_tacho(self):
        return self.tachometer.get_tacho()

    def get_cap(self):
        return self.gyro.get_cap()

    def has_gyro_data(self):
        return True

    def setLed(self, etat):
        pass

    def getBoutonPoussoir(self):
        return 1

    def gpioCleanUp(self):
        pass
