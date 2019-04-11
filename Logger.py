class Logger:

    def __init__(self, simulator, simu_time, image_analyser, speed_controller, voiture, arduino, asservissement, sequenceur):
        self.simu_time = simu_time
        self.image_analyser = image_analyser
        self.sequenceur = sequenceur
        self.asservissement = asservissement
        self.arduino = arduino
        self.voiture = voiture
        self.speed_controller = speed_controller
        self.simulator = simulator

    def execute(self):
        self.log()

    def log(self):
        print("tacho : %s" % self.speed_controller.get_tacho())
        print("Simu time : %fs " % self.simu_time.time())


