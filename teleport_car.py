import time

from robot.Simulator import Simulator

simulation_duration_seconds = 5

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

simulator.start_simulation()
start_time = time.time()

while time.time() - start_time < simulation_duration_seconds:
    start_step_time = time.time()
    # [component.execute() for component in executable_components]
    print("code execution time : %fs " % (time.time() - start_step_time))
    simulator.set_target_speed(handles["left_motor"], -50)
    simulator.set_target_speed(handles["right_motor"], - 50)
    start_simulator_step_time = time.time()
    simulator.do_simulation_step()
    print("simulator execution time : %fs " % (time.time() - start_simulator_step_time))


start_time = time.time()

simulator.teleport_to_start_pos()

while time.time() - start_time < simulation_duration_seconds:
    start_step_time = time.time()
    # [component.execute() for component in executable_components]
    print("code execution time : %fs " % (time.time() - start_step_time))
    simulator.set_target_speed(handles["left_motor"], -50)
    simulator.set_target_speed(handles["right_motor"], - 50)
    start_simulator_step_time = time.time()
    simulator.do_simulation_step()
    print("simulator execution time : %fs " % (time.time() - start_simulator_step_time))


simulator.stop_simulation()
