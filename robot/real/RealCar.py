from robot.Car import Car


class RealCar(Car):

    RPM_MAX_VOITURE_IMMOBILE = 200  # RPM en dessous duquel on considère la voiture immobile

    def __init__(self, steering_controller, motors_handles, speed_controller, tachometer, gyro, camera, time, arduino):
        super().__init__(steering_controller, motors_handles, speed_controller, tachometer, gyro, camera, time)
        self.arduino = arduino

    def set_led(self, etat):
        if self.led_state != etat:
            st = "*\n{:d}\n".format(etat)
            self.arduino.ser.write(bytes(st, 'utf-8'))
            self.led_state = etat

    def set_chenillard(self, etat):
        if self.chenillard_state != etat:
            st = "/\n{:d}\n".format(etat)
            self.arduino.ser.write(bytes(st, 'utf-8'))
            self.chenillard_state = etat

    def has_gyro_data(self):
        return self.arduino.nouvelleDonneeGyro

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
