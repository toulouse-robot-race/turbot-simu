from robot.Car import Car


class RealCar(Car):

    RPM_MAX_VOITURE_IMMOBILE = 200  # RPM en dessous duquel on considère la voiture immobile

    def __init__(self, steering_controller, speed_controller, tachometer, gyro, camera, time, arduino):
        super().__init__(steering_controller, speed_controller, tachometer, gyro, camera, time)
        self.arduino = arduino
        self.led_state = False
        self.chenillard_state = False

    def set_led(self, state: bool):
        if self.led_state != state:
            self.arduino.set_led(state)

    def set_chenillard(self, state: bool):
        if self.chenillard_state != state:
            self.arduino.set_chenillard(state)

    def has_gyro_data(self):
        return self.arduino.nouvelleDonneeGyro

    def check_gyro_stable(self):
        return self.arduino.checkGyroStable()

    def get_push_button(self):
        return self.arduino.button

    def gpioCleanUp(self):
        pass

    def freine(self):
        self.speedController.set_speed_percent(0)
        self.speedController.send_brake_command()

    def isMotionLess(self):
        return -self.RPM_MAX_VOITURE_IMMOBILE < self.speedController.rpm < self.RPM_MAX_VOITURE_IMMOBILE

    def reverse(self):
        self.speedController.set_reverse()

    def send_display(self, string):
        self.arduino.send_display(string)
