WHEEL_SIZE = 0.05
RAD_TO_DEG = 57.2958
STEERING_COEF = -0.0285
SPEED_COEF = 11 / -WHEEL_SIZE / 100 # First number is speed in m/s for 100%
TACHO_COEF = 205  # Number of tachometer increments for 1 meter
GYRO_COEF = -RAD_TO_DEG
SIMU_STEP_TIME = 0.05
NB_IMAGES_DELAY = 2
CAMERA_DELAY = NB_IMAGES_DELAY * SIMU_STEP_TIME