from robot import Config
from vrep import b0RemoteApi

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

    def set_target_pos(self, joint_handle, target_pos):
        self.client.simxSetJointTargetPosition(joint_handle, target_pos, self.client.simxDefaultPublisher())

    def set_target_speed(self, joint_handle, target_speed):
        self.client.simxSetJointTargetVelocity(joint_handle, target_speed, self.client.simxDefaultPublisher())

    def get_joint_angular_speed(self, joint):
        angular_speed = self.get_object_float_parameter(joint, JOINT_VELOCITY_PARAMETER)
        return angular_speed if angular_speed is not None else 0

    simulation_time = 0

    def get_simulation_time(self):
        if self.simulation_time == 0:
            def callback(result):
                self.simulation_time = round(result[1], 3)

            self.client.simxGetSimulationTime(self.client.simxDefaultSubscriber(callback))

        return self.simulation_time

    def get_simulation_time_step(self):
        return self.client.simxGetSimulationTimeStep(self.client.simxServiceCall())[1]

    signals = {}

    def get_float_signal(self, signal_name):
        if signal_name not in self.signals:
            def callback(result):
                self.signals[signal_name] = result[1]

            self.signals[signal_name] = None
            self.client.simxGetFloatSignal(signal_name, self.client.simxDefaultSubscriber(callback))

        return self.signals[signal_name]

    parameters = {}

    def get_object_float_parameter(self, object_handle, parameter):
        if object_handle not in self.parameters:
            self.parameters[object_handle] = {}
            self.parameters[object_handle][parameter] = None

            def callback(result):
                self.parameters[object_handle][parameter] = result[1]

            self.client.simxGetObjectFloatParameter(object_handle, parameter,
                                                    self.client.simxDefaultSubscriber(callback))

        return self.parameters[object_handle][parameter]

    images = {}

    def get_gray_image(self, vision_sensor_handle):
        if not self.images:
            def callback(result):
                self.images[self.simulation_time] = result[1:]

            self.client.simxGetVisionSensorImage(vision_sensor_handle, True,
                                                 self.client.simxDefaultSubscriber(callback))
        if self.simulation_time - Config.CAMERA_DELAY in self.images:
            return self.images[self.simulation_time - Config.CAMERA_DELAY]
        else:
            return None, None

    positions = {}

    def get_object_position(self, object_handle):
        if object_handle not in self.positions:
            self.positions[object_handle] = None

            def callback(result):
                self.positions[object_handle] = result[1]

            self.client.simxGetObjectPosition(object_handle, -1, self.client.simxDefaultSubscriber(callback))
        return self.positions[object_handle]

    orientations = {}

    def get_object_orientation(self, object_handle):
        if object_handle not in self.orientations:
            self.orientations[object_handle] = None

            def callback(result):
                self.orientations[object_handle] = result[1]

            self.client.simxGetObjectOrientation(object_handle, -1, self.client.simxDefaultSubscriber(callback))
        return self.orientations[object_handle]
