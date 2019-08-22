from robot.Component import Component


class Tachometer(Component):

    def __init__(self, vesc):
        self.vesc = vesc
        self.delta_tacho = 0
        self.tacho = None
        self.first_tacho = None

    def execute(self):
        self.compute_tacho()

    def compute_tacho(self):
        next_tacho = self.vesc.request_data()[0]

        if next_tacho == 0:
            return

        if self.first_tacho is None:
            self.first_tacho = next_tacho
        elif self.tacho is None:
            self.delta_tacho = next_tacho - self.first_tacho
        else:
            self.delta_tacho = next_tacho - self.tacho

        self.tacho = next_tacho

    def get_tacho(self):
        if self.first_tacho is None or self.tacho is None:
            return 0
        else:
            return self.tacho - self.first_tacho

    def get_delta_tacho(self):
        return self.delta_tacho

    def reset(self):
        self.tacho = 0
        self.delta_tacho = 0
        self.first_tacho = None
