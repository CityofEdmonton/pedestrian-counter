import pygame
import os
import math
import time
from datetime import datetime, date
import numpy as np
from scipy.interpolate import griddata
from scipy import stats
import cv2
from colour import Color
from CentroidTracker import CentroidTracker
from multiprocessing import Process, active_children
import pexpect
import argparse
import busio
import board
import adafruit_amg88xx
import json
import gpsd
import threading
import sys
# some utility functions


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# separate process using pexpect to interact with ttn transmission


def transmit(str):
    dir = os.path.dirname(__file__)
    filename = os.path.join(dir, './ttn/thethingsnetwork-send-v1')
    lora = pexpect.spawn(filename)
    while(1):
        # handle all cases
        i = lora.expect(['waiting', 'FAILURE', 'not sending',
                         pexpect.TIMEOUT, pexpect.EOF])
        if i == 0:
            lora.sendline(str)
            print('PedCount updated!\n')
            lora.terminate(force=True)
            break
        else:
            print('Lora Failure: retrying...')


def send_lora(delay):
    global payload
    while True:
        for child in active_children():
            if child.name == 'lora_proc':
                child.terminate()
        loraproc = Process(
            target=transmit, name='lora_proc', args=(json.dumps(payload), ))
        loraproc.start()
        time.sleep(delay)

# a - latitude
# o - longitude
# c - count
payload = {'a': 0, 'o': 0, 'c': 0}


def main():
    global payload
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "color_depth", help="integer number of colors to use to draw temps", type=int)
    parser.add_argument(
        '--headless', help='run the pygame headlessly', action='store_true')
    args = parser.parse_args()
    gpsd.connect()
    i2c_bus = busio.I2C(board.SCL, board.SDA)

    MAXTEMP = 29  # initial max temperature
    COLORDEPTH = args.color_depth  # how many color values we can have
    AMBIENT_OFFSET = 9  # value to offset ambient temperature by to get rolling MAXTEMP
    # length of ambient temperature collecting intervals increments of 0.1 seconds
    AMBIENT_TIME = 100
    LORA_SEND_INTERVAL = 1  # length of intervals between attempted lora uplinks in seconds

    if args.headless:
        os.putenv('SDL_VIDEODRIVER', 'dummy')
    else:
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
    blue = Color("blue")
    colors = list(blue.range_to(Color("yellow"), COLORDEPTH))

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
    params.minArea = 250

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
    mode_list = []

    send_thread = threading.Thread(
        target=send_lora, args=(LORA_SEND_INTERVAL,))
    send_thread.start()

    while(True):
        start = time.time()
        # read the pixels

        pixels = []

        for row in sensor.pixels:
            pixels = pixels + row

        mode_result = stats.mode([round(p) for p in pixels])
        mode_list.append(int(mode_result[0]))

        MAXTEMP = float(np.mean(mode_list)) + AMBIENT_OFFSET
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
                    print("Caught drawing error")
        pygame.display.update()

        surface = pygame.display.get_surface()
        myfont = pygame.font.SysFont("comicsansms", 32)

        img = pygame.surfarray.array3d(surface)
        img = np.swapaxes(img, 0, 1)

        # Read image
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.bitwise_not(img)

        # Detect blobs.
        keypoints = detector.detect(img)
        img_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        for i in range(0, len(keypoints)):
            x = keypoints[i].pt[0]
            y = keypoints[i].pt[1]

            # print circle around blobs
            pygame.draw.circle(lcd, (200,0,0), (int(x), int(y)), round(keypoints[i].size), 2)

        # update counter in top left
        textsurface = myfont.render(str(ct.get_count()), False, (0, 0, 0))
        lcd.blit(textsurface,(0,0))

        # update  our centroid tracker using the detected centroids
        ct.update(keypoints)

        pygame.display.update()

        time.sleep(max(1./25 - (time.time() - start), 0))

        packet = gpsd.get_current()

        payload['a'] = round(packet.lat, 3)
        payload['o'] = round(packet.lon, 3)
        payload['c'] = ct.get_count()

        # empty mode_list every AMBIENT_TIME *10 seconds to get current ambient temperature
        if len(mode_list) > AMBIENT_TIME:
            mode_list = []

    print("terminating...")


if __name__ == "__main__":
    main()
