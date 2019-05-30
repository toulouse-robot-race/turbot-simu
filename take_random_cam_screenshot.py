import os
import random
import time

import numpy as np

from robot.Simulator import Simulator

simulation_duration_seconds = 40

simulator = Simulator()

current_dir = os.path.dirname(os.path.realpath(__file__))


handles = {
    "right_motor": simulator.get_handle("driving_joint_rear_right"),
    "left_motor": simulator.get_handle("driving_joint_rear_left"),
    "left_steering": simulator.get_handle("steering_joint_fl"),
    "right_steering": simulator.get_handle("steering_joint_fr"),
    "cam": simulator.get_handle("Vision_sensor"),
    "base_car": simulator.get_handle("base_link"),
    "track": simulator.get_handle("TRR_track")
}
simulator.start_simulation()
start_time = time.time()

pos = None
orientation = None
while time.time() - start_time < simulation_duration_seconds:
    if pos is None:
        pos = simulator.get_object_position(handles['base_car'])
        orientation = simulator.get_object_orientation(handles['base_car'])
    else:
        pos[1] = random.uniform(20, 22)
        pos[0] = random.uniform(-3, -1)
        orientation[2] = random.uniform(3.10,3.14)
        simulator.set_object_pos(handles["base_car"], pos)
        simulator.set_object_orientation(handles["base_car"], orientation)
        resolution, byte_array_image_string = simulator.get_gray_image(handles["cam"], 0)
        if resolution is not None and byte_array_image_string is not None:
            image_numpy = np.flipud(np.fromstring(byte_array_image_string, dtype=np.uint8).reshape(resolution[::-1]))
            if image_numpy.mean() > 1:
                np.save(os.path.join(current_dir, "pictures", str(time.time())), image_numpy)

    simulator.do_simulation_step()
simulator.stop_simulation()
