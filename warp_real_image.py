# Init camera stream
import cv2

from robot.ImageWarper import ImageWarper
from robot.real.UsbCam import UsbCam

usbCam = UsbCam()
imageWarper = ImageWarper(None, 0, 0, translation_enabled=False, rotation_enabled=False)

while True:
    frame = usbCam.read()
    warped = imageWarper.warp(frame)
    cv2.imshow("original", frame)
    cv2.imshow("perspective warped", warped)
    cv2.waitKey(10)
