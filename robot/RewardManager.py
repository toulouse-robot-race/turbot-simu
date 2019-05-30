import numpy as np


class RewardManager:
    BEGIN_POS_PHASE_1 = [-1, 5, 0]
    BEGIN_POS_PHASE_2 = [-1, 23.5, 0]
    BEGIN_POS_PHASE_3 = [1, 23.5, 0]
    BEGIN_POS_PHASE_4 = [1, -23.5, 0]
    BEGIN_POS_PHASE_5 = [-1, -23.5, 0]

    END_Y_PHASE_1 = BEGIN_POS_PHASE_2[1]
    END_X_PHASE_2 = BEGIN_POS_PHASE_3[0]
    END_Y_PHASE_3 = BEGIN_POS_PHASE_4[1]
    END_X_PHASE_4 = BEGIN_POS_PHASE_5[0]
    END_Y_PHASE_5 = BEGIN_POS_PHASE_1[1]

    def __init__(self):
        self.previous_pos = self.BEGIN_POS_PHASE_1
        self.phase = 1

    def is_end_phase_1(self, pos):
        return self.phase == 1 and pos[1] >= self.END_Y_PHASE_1

    def is_end_phase_2(self, pos):
        return self.phase == 2 and pos[0] >= self.END_X_PHASE_2

    def is_end_phase_3(self, pos):
        return self.phase == 3 and pos[1] <= self.END_Y_PHASE_3

    def is_end_phase_4(self, pos):
        return self.phase == 4 and pos[0] <= self.END_X_PHASE_4

    def is_end_phase_5(self, pos):
        return self.phase == 5 and pos[1] >= self.END_Y_PHASE_5

    def get_reward(self, pos):
        reward = 0.0

        if self.is_end_phase_1(pos):
            self.phase += 1
            reward += self.END_Y_PHASE_1 - self.previous_pos[1]
            self.previous_pos = self.BEGIN_POS_PHASE_2
        elif self.is_end_phase_2(pos):
            self.phase += 1
            reward += self.END_X_PHASE_2 - self.previous_pos[0]
            self.previous_pos = self.BEGIN_POS_PHASE_3
        elif self.is_end_phase_3(pos):
            self.phase += 1
            reward += self.END_Y_PHASE_3 - self.previous_pos[0]
            self.previous_pos = self.BEGIN_POS_PHASE_4
        elif self.is_end_phase_4(pos):
            self.phase += 1
            reward += self.END_X_PHASE_4 - self.previous_pos[0]
            self.previous_pos = self.BEGIN_POS_PHASE_5
        elif self.is_end_phase_5(pos):
            self.phase = 0
            reward += self.END_Y_PHASE_5 - self.previous_pos[0]
            self.previous_pos = self.BEGIN_POS_PHASE_1

        delta_pos = np.array(pos) - np.array(self.previous_pos)
        self.previous_pos = pos

        if self.phase == 1:
            reward += delta_pos[1]
        elif self.phase == 2:
            reward += delta_pos[0]
        elif self.phase == 3:
            reward += -delta_pos[1]
        elif self.phase == 4:
            reward += -delta_pos[0]
        elif self.phase == 5:
            reward += delta_pos[1]


        return reward
