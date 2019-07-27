from robot.Component import Component


class Tachometer(Component):

    def __init__(self, vesc):
        self.vesc = vesc
        self.delta_tacho = 0
        self.tacho = 0
        self.previous_pos = None

    def execute(self):
        self.compute_tacho()

    def compute_tacho(self):
        next_tacho = self.vesc.request_data()[0]
        self.delta_tacho = next_tacho - self.tacho
        self.tacho = next_tacho

    def get_tacho(self):
        return self.tacho

    def get_delta_tacho(self):
        return self.delta_tacho

    def reset(self):
        self.tacho = 0
        self.delta_tacho = 0
        self.previous_pos = None
