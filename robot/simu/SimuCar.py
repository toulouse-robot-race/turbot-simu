from robot.Car import Car


class SimuCar(Car):

    def set_led(self, etat):
        pass

    def set_chenillard(self, etat):
        pass

    def has_gyro_data(self):
        return True

    def setLed(self, etat):
        pass

    def get_push_button(self):
        pass

    def gpioCleanUp(self):
        pass

    def freine(self):
        self.speedController.set_speed_target(0)

    def isMotionLess(self):
        return self.tachometer.get_delta_tacho() < 1

    def reverse(self):
        return self.speedController.set_speed_target(-10)
