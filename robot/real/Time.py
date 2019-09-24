import time


class Time:

    @staticmethod
    def time():
        return time.time()

    @staticmethod
    def sleep(duration):
        time.sleep(duration)
