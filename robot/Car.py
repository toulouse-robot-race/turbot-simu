class Car:

    def __init__(self, steering_controller, motors_handles, speed_controller, tachometer, gyro, camera, time):
        self.steering_controller = steering_controller
        self.camera = camera
        self.time = time
        self.gyro = gyro
        self.tachometer = tachometer
        self.motors_handles = motors_handles
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

    def has_gyro_data(self):
        return True

    def setLed(self, etat):
        pass

    def getBoutonPoussoir(self):
        return 1

    def gpioCleanUp(self):
        pass

    def freine(self):
        self.speedController.set_speed_target(0)

    def isMotionLess(self):
        return self.tachometer.get_delta_tacho() < 1

    def reverse(self):
        return self.speedController.set_speed_target(-10)
