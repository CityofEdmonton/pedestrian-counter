import numpy as np
import math
import time
from matplotlib import pyplot as plt
from Adafruit_AMG88xx import Adafruit_AMG88xx
from scipy.interpolate import griddata
import cv2

# Start sensor
sensor = Adafruit_AMG88xx()

active = True

while(1):
    if active == True:
        # Read pixels, convert them to values between 0 and 1, map them to an 8x8 grid
        pixels = sensor.readPixels()
        pixmax = max(pixels)
        pixels = [x / pixmax for x in pixels]
        points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
        grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]

        # bicubic interpolation of 8x8 grid to make a 32x32 grid
        bicubic = griddata(points, pixels, (grid_x, grid_y), method='cubic')
        image = np.array(bicubic)
        image = np.reshape(image, (32, 32))
        plt.imsave('color_img.jpg', image)

        # Read image
        img = cv2.imread("color_img.jpg", cv2.IMREAD_GRAYSCALE)
        img = cv2.bitwise_not(img)

        # Setup SimpleBlobDetector parameters.
        params = cv2.SimpleBlobDetector_Params()

        # Change thresholds
        params.minThreshold = 10
        params.maxThreshold = 255

        # Filter by Area.
        params.filterByArea = True
        params.minArea = 5

        # Filter by Circularity
        params.filterByCircularity = True
        params.minCircularity = 0.1

        # Filter by Convexity
        params.filterByConvexity = False
        params.minConvexity = 0.87

        # Filter by Inertia
        params.filterByInertia = False
        params.minInertiaRatio = 0.01

        # Set up the detector with default parameters.
        detector = cv2.SimpleBlobDetector_create(params)

        # Detect blobs.
        keypoints = detector.detect(img)

        for i in range (0, len(keypoints)):
            x = keypoints[i].pt[0]
            y = keypoints[i].pt[1]
            print(x, y)

print("closing...")
