import pygame
import os
import math
import datetime
from datetime import datetime, date
import time
import numpy as np
from scipy.interpolate import griddata
from scipy import stats
import cv2
from colour import Color
from CentroidTracker import CentroidTracker
from multiprocessing import Process, active_children
import pexpect
import busio
import board
import adafruit_amg88xx
import functools
from functools import cmp_to_key
import json
# some utility functions


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Numerically sorts filenames


def image_sort(x, y):
    x = int(x.split(".")[0])
    y = int(y.split(".")[0])
    return x-y


def main():

    # empty the images folder
    for filename in os.listdir('../img/'):
        if filename.endswith('.jpeg'):
            os.unlink('../img/' + filename)

    i2c_bus = busio.I2C(board.SCL, board.SDA)
    MAXTEMP = 31
    # how many color values we can have
    COLORDEPTH = 1024

    # For headless pygame
    #os.putenv('SDL_VIDEODRIVER', 'dummy')

    # For displaying pygame
    os.putenv('SDL_FBDEV', '/dev/fb1')
    pygame.init()

    # initialize the sensor
    sensor = adafruit_amg88xx.AMG88XX(i2c_bus)

    points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
    grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]

    # sensor is an 8x8 grid so lets do a square
    height = 240
    width = 240

    # the list of colors we can choose from
    blue = Color("indigo")
    colors = list(blue.range_to(Color("red"), COLORDEPTH))

    # create the array of colors
    colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255))
              for c in colors]

    displayPixelWidth = width / 30
    displayPixelHeight = height / 30

    lcd = pygame.display.set_mode((width, height))

    lcd.fill((255, 0, 0))

    pygame.display.update()
    pygame.mouse.set_visible(False)

    lcd.fill((0, 0, 0))
    pygame.display.update()

    # Setup SimpleBlobDetector parameters.
    params = cv2.SimpleBlobDetector_Params()

    # # Change thresholds
    params.minThreshold = 10
    params.maxThreshold = 255

    # # Filter by Area.
    params.filterByArea = True
    params.minArea = 5

    # # Filter by Circularity
    params.filterByCircularity = True
    params.minCircularity = 0.1

    # # Filter by Convexity
    params.filterByConvexity = False
    params.minConvexity = 0.87

    # # Filter by Inertia
    params.filterByInertia = False
    params.minInertiaRatio = 0.01

    # # Set up the detector with default parameters.
    detector = cv2.SimpleBlobDetector_create(params)

    # initialize centroid tracker
    ct = CentroidTracker()

    # let the sensor initialize
    time.sleep(.1)
    frame = 0

    # press key to exit
    screencap = True

    # json dump
    data = {}
    data['sensor_readings'] = []

    while(screencap):
        start = time.time()
        # read the pixels

        pixels = []
        for row in sensor.pixels:
            pixels = pixels + row

        data['sensor_readings'].append({
            'time': datetime.now().isoformat(),
            'temps': pixels
        })
        mode_result = stats.mode([round(p) for p in pixels])

        if MAXTEMP <= mode_result[0]:
            MAXTEMP = 37

        pixels = [map_value(p, mode_result[0]+2, MAXTEMP, 0,
                            COLORDEPTH - 1) for p in pixels]

        # perform interpolation
        bicubic = griddata(points, pixels, (grid_x, grid_y), method='cubic')

        # draw everything
        for ix, row in enumerate(bicubic):
            for jx, pixel in enumerate(row):
                try:
                    pygame.draw.rect(lcd, colors[constrain(int(pixel), 0, COLORDEPTH - 1)],
                                     (displayPixelHeight * ix, displayPixelWidth * jx, displayPixelHeight, displayPixelWidth))
                except:
                    pass
        pygame.display.update()

        surface = pygame.display.get_surface()

        # frame saving
        folder = '../img/'
        filename = str(frame) + '.jpeg'
        pygame.image.save(surface, folder + filename)

        img = pygame.surfarray.array3d(surface)
        img = np.swapaxes(img, 0, 1)

        # Read image
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.bitwise_not(img)

        # Detect blobs.
        keypoints = detector.detect(img)

        for i in range(0, len(keypoints)):
            x = keypoints[i].pt[0]
            y = keypoints[i].pt[1]

            # print little circle
            pygame.draw.circle(lcd, (200, 0, 0), (int(x), int(y)), 7, 3)

        # update  our centroid tracker using the detected centroids
        ct.update(keypoints)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                print('terminating...')
                screencap = False
                break
        frame += 1
        time.sleep(max(1./25 - (time.time() - start), 0))

    # stitch the frames together
    dir_path = '../img'
    ext = '.jpeg'

    out_index = 0
    while os.path.exists('../video/output%s.mp4' % out_index):
        out_index += 1
    output = str('../video/output%s.mp4' % out_index)

    framerate = 10

    # get files from directory
    images = []
    for f in os.listdir(dir_path):
        if f.endswith(ext):
            images.append(f)

    # sort files
    images = sorted(images, key=cmp_to_key(image_sort))

    # determine width and height from first image
    image_path = os.path.join(dir_path, images[0])
    frame = cv2.imread(image_path)
    cv2.imshow('video', frame)
    height, width, channels = frame.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Be sure to use lower case
    out = cv2.VideoWriter(output, fourcc, framerate, (width, height))

    for image in images:

        image_path = os.path.join(dir_path, image)
        frame = cv2.imread(image_path)

        out.write(frame)  # Write out frame to video

        cv2.imshow('video', frame)
        if (cv2.waitKey(1) & 0xFF) == ord('q'):  # Hit `q` to exit
            break

    # Release everything if job is finished
    out.release()
    cv2.destroyAllWindows()
 
    data_index = 0
    while os.path.exists('../data/data%s.json' % data_index):
        data_index += 1
    data_path = str('../data/data%s.json' % data_index)

    with open(data_path, 'w+') as outfile:
        json.dump(data, outfile, indent=4)


if __name__ == "__main__":
    main()
