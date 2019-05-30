from robot.Config import GYRO_COEF


class Gyro:
    def __init__(self, simulator, gyro_name):
        self.gyro_name = gyro_name
        self.simulator = simulator
        self.step_time = simulator.get_simulation_time_step()
        self.gyro = float(0)
        self.delta_gyro = float(0)

    def execute(self):
        self.compute_gyro()

    def get_cap(self):
        return self.gyro

    def get_delta_cap(self):
        return self.delta_gyro

    def get_gyro_variation_step(self):
        if self.simulator.get_float_signal(self.gyro_name) is not None:
            return self.simulator.get_float_signal(self.gyro_name) * GYRO_COEF
        else:
            return 0

    def compute_gyro(self):
        self.delta_gyro = self.get_gyro_variation_step()
        self.gyro += self.delta_gyro

    def reset(self):
        self.gyro = float(0)
        self.delta_gyro = float(0)