from robot.Config import GYRO_COEF


class Gyro:
    def __init__(self, simulator, base_car):
        self.base_car = base_car
        self.simulator = simulator
        self.step_time = simulator.get_simulation_time_step()
        self.gyro = -180

    def execute(self):
        self.compute_gyro()

    def get_cap(self):
        return self.gyro

    def compute_gyro(self):
        orientation = self.simulator.get_object_orientation(self.base_car)
        if orientation is None:
            return
        self.gyro = orientation[2] * GYRO_COEF
