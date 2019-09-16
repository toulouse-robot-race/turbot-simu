#!/usr/bin/env python3
import time
from pathlib import Path

from robot import Programs
from robot.ImageAnalyzer import ImageAnalyzer
from robot.ImageWarper import ImageWarper
from robot.Sequencer import Sequencer
from robot.real.Arduino import Arduino
from robot.real.Camera import Camera
from robot.real.Config import NB_IMAGES_DELAY
from robot.real.Gyro import Gyro
from robot.real.RealCar import RealCar
from robot.real.SpeedController import SpeedController
from robot.real.SteeringController import SteeringController
from robot.real.Tachometer import Tachometer
from robot.real.Time import Time
from robot.real.Vesc import Vesc
from robot.simu.Config import TACHO_COEF
from robot.strategy.StrategyFactory import StrategyFactory

RAM_DISK_DIR = "/tmp_ram"

MASK_LINE_FILE = RAM_DISK_DIR + "/mask_line.npy"

MASK_OBSTACLE_FILE = RAM_DISK_DIR + "/mask_obstacle.npy"

if not Path(MASK_OBSTACLE_FILE).is_file() or not Path(MASK_LINE_FILE).is_file():
    raise Exception("Inference is not launched")

real_time = Time()

arduino = Arduino()

vesc = Vesc(serial_device="/dev/ttyACM0")

steering_controller = SteeringController(arduino=arduino)

speed_controller = SpeedController(vesc=vesc,
                                   enable=True)

gyro = Gyro(arduino=arduino)

tachometer = Tachometer(vesc=vesc)

camera = Camera(MASK_LINE_FILE, MASK_OBSTACLE_FILE)

car = RealCar(steering_controller=steering_controller,
              speed_controller=speed_controller,
              tachometer=tachometer,
              gyro=gyro,
              camera=camera,
              time=real_time,
              arduino=arduino)

image_warper = ImageWarper(car=car, nb_images_delay=NB_IMAGES_DELAY, tacho_coef=TACHO_COEF, rotation_enabled=True)

image_analyzer = ImageAnalyzer(car=car,
                               image_warper=image_warper,
                               show_and_wait=False)


strategy_factory = StrategyFactory(car, image_analyzer)

sequencer = Sequencer(car=car,
                      program=Programs.TEST,
                      strategy_factory=strategy_factory)


# Order matter, components will be executed one by one
executable_components = [arduino,
                         gyro,
                         tachometer,
                         camera,
                         sequencer,
                         speed_controller,
                         steering_controller]

# Time needed by the serials connections to get ready
time.sleep(1)
while True:
    [component.execute() for component in executable_components]
    # Time needed by arduino to receive next command
    time.sleep(0.005)
