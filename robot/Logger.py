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

    def execute(self):
        self.log()

    def log(self):
        print("tacho : %s" % self.tachometer.get_tacho())
        print("Simu time : %fs " % self.time.time())
        # print("orientation : %s" % str(self.simulator.get_object_orientation(self.handles["base_car"])))


