from robot.Component import Component


class Gyro(Component):
    def __init__(self, arduino):
        self.arduino = arduino

    gyro = float(0)
    delta_gyro = float(0)

    def execute(self):
        next_gyro = self.arduino.get_cap()
        self.delta_gyro = next_gyro - self.gyro
        self.gyro = next_gyro

    def get_cap(self):
        return self.gyro

    def get_delta_cap(self):
        return self.delta_gyro
