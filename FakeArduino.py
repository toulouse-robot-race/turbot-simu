class Arduino:

    def __init__(self, simulator, gyro_name):
        self.gyro_name = gyro_name
        self.simulator = simulator
        self.nouvelleDonneeGyro = True
        self.step_time = simulator.get_simulation_time_step()
        self.gyro = float(0)

    def getCap(self):
        return self.gyro

    def annuleRecalageCap(self):
        pass

    def get_gyro_variation_step(self):
        if self.simulator.get_float_signal(self.gyro_name) is not None:
            return self.simulator.get_float_signal(self.gyro_name) * 57.2958
        else:
            return 0

    def compute_gyro(self):
        self.gyro += self.get_gyro_variation_step()