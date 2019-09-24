import cv2

from robot.real.Config import CAM_HEIGHT, CAM_WIDTH, CAM_HANDLE


class UsbCam:
    stream = cv2.VideoCapture(CAM_HANDLE)
    stream.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    stream.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

    def read(self):
        return self.stream.read()[1]
