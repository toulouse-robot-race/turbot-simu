class Time:
    def __init__(self, simulator):
        self.simulator = simulator

    def time(self):
        return self.simulator.get_simulation_time()

    def sleep(self):
        pass