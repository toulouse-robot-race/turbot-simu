from abc import ABC, abstractmethod


class Car(ABC):

    def __init__(self, steering_controller, speed_controller, tachometer, gyro, camera, time):
        self.steering_controller = steering_controller
        self.camera = camera
        self.time = time
        self.gyro = gyro
        self.tachometer = tachometer
        self.speedController = speed_controller

    def turn(self, steering_input):
        self.steering_controller.steering = steering_input

    def forward(self, speed):
        self.speedController.set_speed_percent(speed)

    def get_tacho(self):
        return self.tachometer.get_tacho()

    def get_delta_tacho(self):
        return self.tachometer.get_delta_tacho()

    def get_cap(self):
        return self.gyro.get_cap()

    def get_delta_cap(self):
        return self.gyro.get_delta_cap()

    def get_time(self):
        return self.time.time()

    def get_images(self):
        return self.camera.mask_line, self.camera.mask_obstacles

    def sleep(self, delay):
        return self.time.sleep(delay)

    @abstractmethod
    def set_led(self, etat):
        pass

    @abstractmethod
    def set_chenillard(self, etat):
        pass

    @abstractmethod
    def has_gyro_data(self):
        pass

    @abstractmethod
    def get_push_button(self):
        pass

    @abstractmethod
    def gpioCleanUp(self):
        pass

    @abstractmethod
    def freine(self):
        pass

    @abstractmethod
    def isMotionLess(self):
        pass

    @abstractmethod
    def reverse(self):
        pass