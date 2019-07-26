from robot.Car import Car


class RealCar(Car):

    def __init__(self, steering_controller, motors_handles, speed_controller, tachometer, gyro, camera, time, arduino):
        super().__init__(steering_controller, motors_handles, speed_controller, tachometer, gyro, camera, time)
        self.arduino = arduino

    def set_led(self, etat):
        pass

    def set_chenillard(self, etat):
        pass

    def has_gyro_data(self):
        pass

    def setLed(self, etat):
        pass

    def get_push_button(self):
        pass

    def gpioCleanUp(self):
        pass

    def freine(self):
        pass

    def isMotionLess(self):
        pass

    def reverse(self):
        pass
