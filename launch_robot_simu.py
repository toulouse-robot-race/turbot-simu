import time

from robot import Programs
from robot.Asservisement import Asservissement
from robot.Camera import Camera
from robot.Car import Car
from robot.Gyro import Gyro
from robot.ImageAnalyzer import ImageAnalyzer
from robot.ImageWarper import ImageWarper
from robot.Logger import Logger
from robot.Sequencer import Sequencer
from robot.Simulator import Simulator
from robot.SpeedController import SpeedController
from robot.Tachometer import Tachometer
from robot.Time import Time

simulation_duration_seconds = 50

simulator = Simulator()

handles = {
    "right_motor": simulator.get_handle("driving_joint_rear_right"),
    "left_motor": simulator.get_handle("driving_joint_rear_left"),
    "left_steering": simulator.get_handle("steering_joint_fl"),
    "right_steering": simulator.get_handle("steering_joint_fr"),
    "line_cam": simulator.get_handle("Vision_sensor_line"),
    "obstacles_cam": simulator.get_handle("Vision_sensor_obstacles"),
    "base_car": simulator.get_handle("base_link")
}

gyro_name = "gyroZ"

simu_time = Time(simulator)

speed_controller = SpeedController(simulator=simulator,
                                   motor_handles=[handles["left_motor"], handles["right_motor"]],
                                   simulation_step_time=simulator.get_simulation_time_step())

gyro = Gyro(simulator=simulator,
            gyro_name=gyro_name)

tachometer = Tachometer(simulator=simulator,
                        base_car=handles['base_car'])


camera = Camera(simulator=simulator,
                line_cam_handle=handles["line_cam"],
                obstacles_cam_handle=handles["obstacles_cam"])

car = Car(simulator=simulator,
          steering_handles=[handles["left_steering"], handles["right_steering"]],
          motors_handles=[handles["left_motor"], handles["right_motor"]],
          speed_controller=speed_controller,
          tachometer=tachometer,
          gyro=gyro,
          camera=camera,
          time=simu_time)


image_warper = ImageWarper(car=car)

image_analyzer = ImageAnalyzer(car=car,
                               image_warper=image_warper,
                               show_and_wait=True)

asservissement = Asservissement(car=car,
                                image_analyzer=image_analyzer)

sequencer = Sequencer(car=car,
                      asservissement=asservissement,
                      image_warper=image_warper,
                      program=Programs.LINE_ANGLE_OFFSET)

logger = Logger(simulator=simulator,
                image_analyzer=image_analyzer,
                car=car,
                asservissement=asservissement,
                sequencer=sequencer,
                handles=handles)

# Order matter, components will be executed one by one
executable_components = [gyro,
                         tachometer,
                         camera,
                         sequencer,
                         asservissement,
                         speed_controller,
                         logger]

simulator.start_simulation()

while simu_time.time() < simulation_duration_seconds:
    start_step_time = time.time()
    [component.execute() for component in executable_components]
    start_simulator_step_time = time.time()
    simulator.do_simulation_step()
