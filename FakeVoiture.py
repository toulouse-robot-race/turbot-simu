import math
import random


class Voiture:

    def __init__(self, simulator, steering_handles, motors_handles, speed_controller, wheel_radius):
        self.motors_handles = motors_handles
        self.steering_handles = steering_handles
        self.simulator = simulator
        self.wheel_radius = wheel_radius
        self.speedController = speed_controller
        self.max_steering = math.pi / 4

    def tourne(self, steering_percent):
        steering_percent += random.randint(-10, 10)
        pos_steering = steering_percent * self.max_steering / 100
        self.simulator.set_target_pos(self.steering_handles[0], pos_steering)
        self.simulator.set_target_pos(self.steering_handles[1], pos_steering)

    def avance(self, speed):
        self.speedController.set_speed_target(speed)

    def setLed(self, etat):
        pass

    def getBoutonPoussoir(self):
        return 1

    def gpioCleanUp(self):
        pass
