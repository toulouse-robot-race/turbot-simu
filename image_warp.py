import glob
import os

import cv2
import numpy as np


def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, cropping

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    print(x, y)


pictures_path = 'pictures'
dirpath = os.getcwd()

files = [f for f in glob.glob(os.path.join(dirpath, pictures_path) + "**/*.npy", recursive=True)]

cv2.namedWindow("image")
cv2.setMouseCallback("image", click_and_crop)

for f in files:
    image_array = np.load(f)
    img = cv2.cvtColor(image_array.astype(np.uint8), cv2.COLOR_BGR2RGB)
    cv2.imshow('image', img)
    cv2.waitKey(0)

    height, width, channels = img.shape
    print(height, width)


    bl = [0, 240]
    br = [320, 240]
    pts1 = np.float32([[100, 60], [220, 60], bl, br])
    pts2 = np.float32([[0, 0], [320, 0], bl, br])
    M = cv2.getPerspectiveTransform(pts1, pts2)

    warped_img = cv2.warpPerspective(img, M, (width, height))

    cv2.imshow('image', warped_img)
    cv2.waitKey(0)
