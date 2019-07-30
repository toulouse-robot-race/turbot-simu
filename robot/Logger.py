from robot.Component import Component


class Logger(Component):

    def __init__(self, simulator, image_analyzer,
                 car, sequencer, handles):
        self.handles = handles
        self.image_analyzer = image_analyzer
        self.sequencer = sequencer
        self.car = car
        self.simulator = simulator
        self.previous_joint_pos = 0
        self.first_pos = None

    def execute(self):
        self.log()

    def log(self):
        print("tacho : %s" % self.car.get_tacho())
        print("Simu time : %fs " % self.car.get_time())
        print("delta gyro", self.car.get_tacho)
        pos = self.simulator.get_object_position(self.handles["base_car"])
        print("car pos", self.simulator.get_object_position(self.handles["base_car"]))
        if pos is not None and self.first_pos is None:
            self.first_pos = pos
        if self.first_pos is not None:
            print("delta x from start", str(pos[0] - self.first_pos[0]))
        delta_tacho = self.car.get_delta_tacho()
        print("delta tacho", delta_tacho)
        joint_pos = self.simulator.get_joint_position(self.handles["right_motor"])
        if joint_pos is not None:
            delta_joint_pos = joint_pos - self.previous_joint_pos
            print("Delta joint pos", delta_joint_pos)
            self.previous_joint_pos = joint_pos
            if delta_tacho is not 0:
                print("joint pos per tacho", delta_joint_pos / delta_tacho)
