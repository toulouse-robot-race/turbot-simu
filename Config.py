import math

WHEEL_SIZE = 0.05
RAD_TO_DEG = 57.2958
STEERING_COEF = (-math.pi / 4) / 100
SPEED_COEF = -1 / WHEEL_SIZE
TACHO_COEF = -WHEEL_SIZE * 100
GYRO_COEF = -RAD_TO_DEG
CAMERA_DELAY = 0.15


def steering_response_ramp(x):
    low_steering_command = 1
    high_steering_command = 2
    low_steering_coef = 1
    high_steering_coef = 2
    if x < low_steering_coef:
        return low_steering_coef
    elif x > high_steering_command:
        return high_steering_command
    else:
        return low_steering_coef + ((x - low_steering_command) / high_steering_command) \
               * (high_steering_coef - low_steering_coef)