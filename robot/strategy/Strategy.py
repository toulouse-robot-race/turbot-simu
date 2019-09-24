from abc import ABC, abstractmethod


class Strategy(ABC):

    @abstractmethod
    def compute_steering(self):
        pass
