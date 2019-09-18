import os
import time

from robot import Programs
from robot.ImageAnalyzer import ImageAnalyzer
from robot.ImageWarper import ImageWarper
from robot.Logger import Logger
from robot.Sequencer import Sequencer
from robot.simu.Camera import Camera
from robot.simu.Config import NB_IMAGES_DELAY, TACHO_COEF
from robot.simu.Gyro import Gyro
from robot.simu.SimuCar import SimuCar
from robot.simu.Simulator import Simulator
from robot.simu.SpeedController import SpeedController
from robot.simu.SteeringController import SteeringController
from robot.simu.Tachometer import Tachometer
from robot.simu.Time import Time
from robot.strategy.StrategyFactory import StrategyFactory

current_dir = os.path.dirname(os.path.realpath(__file__))

simulation_duration_seconds = 50

frame_cycle_log = 5

log_enable=False

simulator = Simulator(log_dir=current_dir + "/simu/logs",
                      log_enable=log_enable,
                      frame_cycle_log=frame_cycle_log)

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

steering_controller = SteeringController(simulator=simulator,
                                         steering_handles=[handles["left_steering"], handles["right_steering"]])

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

car = SimuCar(steering_controller=steering_controller,
              speed_controller=speed_controller,
              tachometer=tachometer,
              gyro=gyro,
              camera=camera,
              time=simu_time)

image_warper = ImageWarper(car=car,
                           nb_images_delay=NB_IMAGES_DELAY,
                           tacho_coef=TACHO_COEF,
                           show_and_wait=False)

image_analyzer = ImageAnalyzer(car=car,
                               image_warper=image_warper,
                               show_and_wait=True)

strategy_factory = StrategyFactory(car, image_analyzer)

sequencer = Sequencer(car=car,
                      program=Programs.LINE_ANGLE_OFFSET,
                      strategy_factory=strategy_factory,
                      image_analyzer=image_analyzer)

logger = Logger(simulator=simulator,
                image_analyzer=image_analyzer,
                car=car,
                sequencer=sequencer,
                image_warper=image_warper,
                steering_controller=steering_controller,
                time=simu_time,
                log_dir=current_dir + "/logs",
                persist_params=log_enable,
                frame_cycle_log=frame_cycle_log)

# Order matter, components will be executed one by one
executable_components = [gyro,
                         tachometer,
                         camera,
                         sequencer,
                         speed_controller,
                         steering_controller,
                         logger]

simulator.start_simulation()

while simu_time.time() < simulation_duration_seconds:
    start_step_time = time.time()
    [component.execute() for component in executable_components]
    start_simulator_step_time = time.time()
    simulator.do_simulation_step()
