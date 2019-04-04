import b0RemoteApi

JOINT_VELOCITY_PARAMETER = 2012


class Simulator:
    def __init__(self):
        self.client = b0RemoteApi.RemoteApiClient('b0RemoteApi_pythonClient', 'b0RemoteApi')
        self.step_done = True
        self.running = True

    def simulation_step_done(self, _):
        self.step_done = True

    def stop_simulation(self):
        self.client.simxStopSimulation(self.client.simxServiceCall())
        self.running = False

    def start_simulation(self):
        self.client.simxSynchronous(True)
        self.client.simxStartSimulation(self.client.simxDefaultPublisher())
        self.client.simxGetSimulationStepDone(self.client.simxDefaultSubscriber(self.simulation_step_done))
        self.running = True

    def do_simulation_step(self):
        if not self.running:
            raise Exception("Simulation not running")
        while not self.step_done:
            self.client.simxSpinOnce()
        self.client.simxSynchronousTrigger()
        self.step_done = False

    def get_handle(self, object_name):
        return self.client.simxGetObjectHandle(object_name, self.client.simxServiceCall())[1]

    def set_target_pos(self, joint_name, target_pos):
        self.client.simxSetJointTargetPosition(joint_name, target_pos, self.client.simxDefaultPublisher())

    def set_target_speed(self, joint_name, target_speed):
        self.client.simxSetJointTargetVelocity(joint_name, target_speed, self.client.simxDefaultPublisher())

    def get_linear_speed(self, handle):
        return self.client.simxGetObjectVelocity(handle, self.client.simxServiceCall())[1]

    def get_joint_angular_speed(self, joint):
        return self.get_object_float_parameter(joint, JOINT_VELOCITY_PARAMETER)

    def get_simulation_time(self):
        return self.client.simxGetSimulationTime(self.client.simxServiceCall())[1]

    def get_simulation_time_step(self):
        return self.client.simxGetSimulationTimeStep(self.client.simxServiceCall())[1]

    def get_float_signal(self, signal_name):
        return self.client.simxGetFloatSignal(signal_name, self.client.simxServiceCall())[1]

    def get_object_float_parameter(self, object_handle, parameter):
        return self.client.simxGetObjectFloatParameter(object_handle, parameter, self.client.simxServiceCall())[1]

    def get_gray_image(self, vision_sensor_name):
        return self.client.simxGetVisionSensorImage(vision_sensor_name, True, self.client.simxServiceCall())[1:]
