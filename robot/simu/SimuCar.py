from robot.Car import Car


class SimuCar(Car):

    def check_gyro_stable(self):
        return True

    def send_display(self, string):
        pass

    def set_led(self, etat: bool):
        pass

    def set_chenillard(self, etat: bool):
        pass

    def has_gyro_data(self):
        return True

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
