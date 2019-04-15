import numpy as np

import Programs
from Logger import Logger
from Simulator import Simulator
from Sequencer import Sequencer
from Car import Car
from Asservisement import Asservissement
from Gyro import Gyro
from ImageAnalyzer import ImageAnalyzer
from Time import Time
from SpeedController import SpeedController
from Tachometer import Tachometer
import time

simulation_duration_seconds = 200

simulator = Simulator()

handles = {
    "right_motor": simulator.get_handle("driving_joint_rear_right"),
    "left_motor": simulator.get_handle("driving_joint_rear_left"),
    "left_steering": simulator.get_handle("steering_joint_fl"),
    "right_steering": simulator.get_handle("steering_joint_fr"),
    "cam": simulator.get_handle("Vision_sensor"),
    "base_car": simulator.get_handle("base_link")
}

gyro_name = "gyroZ"

simu_time = Time(simulator)

image_analyzer = ImageAnalyzer(simulator=simulator,
                               cam_handle=handles["cam"])

speed_controller = SpeedController(simulator=simulator,
                                   motor_handles=[handles["left_motor"], handles["right_motor"]],
                                   simulation_step_time=simulator.get_simulation_time_step())

gyro = Gyro(simulator=simulator,
            gyro_name=gyro_name)

tachometer = Tachometer(simulator=simulator,
                        base_car=handles['base_car'])

car = Car(simulator=simulator,
          steering_handles=[handles["left_steering"], handles["right_steering"]],
          motors_handles=[handles["left_motor"], handles["right_motor"]],
          speed_controller=speed_controller,
          tachometer=tachometer,
          gyro=gyro)

asservissement = Asservissement(car,
                                image_analyzer,
                                simu_time)

sequencer = Sequencer(car,
                      simu_time,
                      asservissement,
                      Programs.TRR)

logger = Logger(simulator,
                simu_time,
                image_analyzer,
                speed_controller,
                car,
                gyro,
                asservissement,
                sequencer,
                handles,
                tachometer)

# Order matter, components will be executed one by one
executable_components = [gyro,
                         tachometer,
                         image_analyzer,
                         sequencer,
                         asservissement,
                         speed_controller,
                         logger]

simulator.start_simulation()

while simu_time.time() < simulation_duration_seconds:
    start_step_time = time.time()
    [component.execute() for component in executable_components]
    print("code execution time : %fs " % (time.time() - start_step_time))

    start_simulator_step_time = time.time()
    simulator.do_simulation_step()
    print("simulator execution time : %fs " % (time.time() - start_simulator_step_time))

simulator.stop_simulation()
