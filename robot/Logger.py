class Logger:

    def __init__(self, simulator, time, image_analyzer, speed_controller,
                 car, gyro, asservissement, sequencer, handles, tachometer):
        self.tachometer = tachometer
        self.handles = handles
        self.time = time
        self.image_analyzer = image_analyzer
        self.sequencer = sequencer
        self.asservissement = asservissement
        self.gyro = gyro
        self.car = car
        self.speed_controller = speed_controller
        self.simulator = simulator
        self.previous_joint_pos = 0

    def execute(self):
        self.log()

    def log(self):
        print("tacho : %s" % self.tachometer.get_tacho())
        print("Simu time : %fs " % self.time.time())
        print("delta gyro", self.gyro.get_delta_cap())
        delta_tacho = self.tachometer.get_delta_tacho()
        print("delta tacho", delta_tacho)
        joint_pos = self.simulator.get_joint_position(self.handles["right_motor"])
        if joint_pos is not None:
            delta_joint_pos = joint_pos - self.previous_joint_pos
            print("Delta joint pos", delta_joint_pos)
            self.previous_joint_pos = joint_pos
            if delta_tacho is not 0:
                print("joint pos per tacho", delta_joint_pos / delta_tacho)
