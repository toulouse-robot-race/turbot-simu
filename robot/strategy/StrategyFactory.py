from robot.strategy.LineAngleOffset import LineAngleOffset


class StrategyFactory:

    def __init__(self, image_analyzer):
        self.image_analyzer = image_analyzer

    def create_lao(self, additional_offset=0):
        return LineAngleOffset(self.image_analyzer, additional_offset)
