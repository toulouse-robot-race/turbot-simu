from robot.strategy.Strategy import Strategy


class CircleStrategy(Strategy):

    def __init__(self, image_analyzer, p_coef):
        self.p_coef = p_coef
        self.image_analyzer = image_analyzer


    def compute_steering(self):

        pass