import math

WHEEL_SIZE = 0.05
RAD_TO_DEG = 57.2958
STEERING_COEF = (-math.pi / 6) / 100 # In radians / 100 for 100%
SPEED_COEF = 9.3 / -WHEEL_SIZE / 100 # First number is speed in m/s for 100%
TACHO_COEF = 205  # Number of tachometer increments for 1 meter
GYRO_COEF = -RAD_TO_DEG
CAMERA_DELAY = 0.10