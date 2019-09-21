import os
import pickle

from robot.Component import Component

LOG_FORMAT = {
    0: "time",
    1: "final image",
    2: "poly coef 1",
    3: "pixel line offset",
    4: "distance obstacle line",
    5: "steering",
    6: "actives rotations",
    7: "actives translations",
    8: "perspective image",
    9: "translated image",
    10: "rotated image"
}


class Logger(Component):

    def __init__(self, image_analyzer,
                 car, sequencer, log_dir,
                 time, steering_controller, image_warper,
                 size_log_stack=5,
                 frame_cycle_log=10,
                 persist_params=False):
        self.persist_params = persist_params
        self.frame_cycle_log = frame_cycle_log
        self.frame_index = 1
        self.image_warper = image_warper
        self.size_log_stack = size_log_stack
        self.steering_controller = steering_controller
        self.time = time
        self.log_dir = log_dir
        self.image_analyzer = image_analyzer
        self.sequencer = sequencer
        self.car = car
        self.previous_joint_pos = 0
        self.first_pos = None
        self.log_array = []
        self.run_session = "run_" + str(time.time())
        self.increment_session = 1
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)

    def execute(self):
        self.log()

    def log(self):

        if self.persist_params:
            if (self.frame_index % self.frame_cycle_log) == 0:
                self.log_array.append([self.time.time(),
                                       self.image_analyzer.final_mask_for_display,
                                       self.image_analyzer.poly_coeff_1,
                                       self.image_analyzer.pixel_offset_line,
                                       self.image_analyzer.distance_obstacle_line,
                                       self.steering_controller.steering,
                                       self.image_warper.actives_rotations,
                                       self.image_warper.actives_translations,
                                       self.image_warper.perspective,
                                       self.image_warper.translated,
                                       self.image_warper.rotated
                                       ])

                if len(self.log_array) >= self.size_log_stack:
                    file_path = self.log_dir + "/" + self.run_session + "_" + "%03d" % self.increment_session + ".pickle"
                    with open(file_path, "wb")as file:
                        pickle.dump(self.log_array, file)

                    self.increment_session += 1
                    self.log_array.clear()

            self.frame_index += 1

