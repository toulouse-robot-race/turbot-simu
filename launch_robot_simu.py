import numpy as np

import Programs
from Logger import Logger
from Simulator import Simulator
from FakeSequenceur import Sequenceur
from FakeVoiture import Voiture
from FakeAsservisement import Asservissement
from FakeArduino import Arduino
from FakeImageAnalyser import ImageAnalyser
from FakeTime import Time
from FakeSpeedController import SpeedController
import time
import signal
import sys

simulation_duration_seconds = 200

simulator = Simulator()

right_motor = simulator.get_handle("driving_joint_rear_right")
right_motor = simulator.get_handle("driving_joint_rear_right")
left_motor = simulator.get_handle("driving_joint_rear_left")
left_steering = simulator.get_handle("steering_joint_fl")
right_steering = simulator.get_handle("steering_joint_fr")
gyro = "gyroZ"
cam = simulator.get_handle("Vision_sensor")
base_car = simulator.get_handle("base_link")

simu_time = Time(simulator)
imageAnalyser = ImageAnalyser(simulator, cam)
speedController = SpeedController(simulator, [left_motor, right_motor],
                                  simulation_step_time=simulator.get_simulation_time_step(),
                                  base_car=base_car)
voiture = Voiture(simulator, [left_steering, right_steering], [left_motor, right_motor],
                  speedController, )
arduino = Arduino(simulator, gyro)
asservissement = Asservissement(arduino, voiture, imageAnalyser, simu_time)
sequenceur = Sequenceur(voiture, simu_time, arduino, asservissement, programme=Programs.course)
logger = Logger(simulator, simu_time, imageAnalyser, speedController, voiture,
                arduino, asservissement, sequenceur)

# Order matter, components will be executed one by one
components = [arduino, sequenceur, imageAnalyser, sequenceur,
              asservissement, speedController, logger]

simulator.start_simulation()

while simu_time.time() < simulation_duration_seconds:
    start_step_time = time.time()
    [component.execute() for component in components]
    print("code execution time : %fs " % (time.time() - start_step_time))

    start_simulator_step_time = time.time()
    simulator.do_simulation_step()
    print("simulator execution time : %fs " % (time.time() - start_simulator_step_time))

simulator.stop_simulation()
