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
import argparse
import csv
import threading
from trackableobject import TrackableObject
# some utility functions



def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def get_filepath(relative_filepath):
    # function to get the absolute filepath of the file you pass in
    dir = os.path.dirname(__file__)
    filename = os.path.join(dir, relative_filepath)
    return filename

def csv_save_append(list):
        datapath = str(get_filepath('../data/') + 'data.csv')
        with open(datapath, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(list)

def csv_save(delay):
    global payload
    while True:
        for child in active_children():
            if child.name == 'csv_proc':
                child.terminate()
        loraproc = Process(
            target=csv_save_append, name='csv_proc', args=(payload, ))
        loraproc.start()
        time.sleep(delay)

payload = [str(datetime.now().isoformat()), 0, 0, 0]

def main():
    global payload

     # argument parsing

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "color_depth", help="integer number of colors to use to draw temps", type=int)
    parser.add_argument(
        '--headless', help='run the pygame headlessly', action='store_true')
    args = parser.parse_args()

    MAXTEMP = 31  # initial max temperature
    COLORDEPTH = args.color_depth  # how many color values we can have
    AMBIENT_OFFSET = 8  # value to offset ambient temperature by to get rolling MAXTEMP
    AMBIENT_TIME = 3000  # length of ambient temperature collecting intervals in seconds

    # create data folders if they don't exist
    if not os.path.exists(get_filepath('../data')):
        os.makedirs(get_filepath('../data'))

    i2c_bus = busio.I2C(board.SCL, board.SDA)

    # For headless pygame
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
    params.minArea = 1000

    # # Filter by Circularity
    params.filterByCircularity = False
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

    # a dictionary to map each unique object ID to a TrackableObject
    trackableObjects = {}

    # the total number of objects that have moved either up or down
    total_down = 0
    total_up = 0
    total_down_old = 0
    total_up_old = 0

    # let the sensor initialize
    time.sleep(.1)

    # press key to exit
    screencap = True

    # array to hold mode of last 10 minutes of temperatures
    mode_list = []

    # thread for saving data
    CSV_SAVE_INTERVAL = 10  # length of intervals between each save
    save_thread = threading.Thread(
        target=csv_save, args=(CSV_SAVE_INTERVAL,))
    save_thread.start()

    print('sensor started!')

    while(screencap):
        start = time.time()

        # read the pixels
        pixels = []
        for row in sensor.pixels:
            pixels = pixels + row

        payload = [str(datetime.now().isoformat()), ct.get_count(), total_up, total_down]

        mode_result = stats.mode([round(p) for p in pixels])
        mode_list.append(int(mode_result[0]))

        # instead of taking the ambient temperature over one frame of data take it over a set amount of time
        MAXTEMP = float(np.mean(mode_list)) + AMBIENT_OFFSET
        pixels = [map_value(p, np.mean(mode_list) + 2, MAXTEMP, 0,
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
        #pygame.display.update()

        surface = pygame.display.get_surface()
        myfont = pygame.font.SysFont("comicsansms", 25)

        img = pygame.surfarray.array3d(surface)
        img = np.swapaxes(img, 0, 1)

        # Read image
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_not = cv2.bitwise_not(img)

        # Detect blobs.
        keypoints = detector.detect(img_not)
        img_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        # draw a horizontal line in the center of the frame -- once an
	    # object crosses this line we will determine whether they were
	    # moving 'up' or 'down'
        pygame.draw.line(lcd, (255, 255, 255), (0, height // 2), (width, height // 2), 2)
        pygame.display.update()

        for i in range(0, len(keypoints)):
            x = keypoints[i].pt[0]
            y = keypoints[i].pt[1]

            # print circle around blob
            pygame.draw.circle(lcd, (200,0,0), (int(x), int(y)), round(keypoints[i].size), 2)

        # update  our centroid tracker using the detected centroids
        objects = ct.update(keypoints)

        # loop over the tracked objects
        for (objectID, centroid) in objects.items():
            # check to see if a trackable object exists for the current
            # object ID
            to = trackableObjects.get(objectID, None)

            # if there is no existing trackable object, create one
            if to is None:
                to = TrackableObject(objectID, centroid)
            
            # otherwise, there is a trackable object so we can utilize it
            # to determine direction
            else:
                # the difference between the y-coordinate of the *current*
                # centroid and the mean of *previous* centroids will tell
                # us in which direction the object is moving (negative for
                # 'up' and positive for 'down')
                y = [c[1] for c in to.centroids]
                direction = centroid[1] - np.mean(y)
                to.centroids.append(centroid)

                # check to see if the object has been counted or not
                if not to.counted:
                    # if the direction is negative (indicating the object
                    # is moving up) AND the centroid is above the center
                    # line, count the object
                    if direction < 0 and centroid[1] < height // 2:
                        total_up += 1
                        to.counted = True

                    # if the direction is positive (indicating the object
                    # is moving down) AND the centroid is below the
                    # center line, count the object
                    elif direction > 0 and centroid[1] > height // 2:
                        total_down += 1
                        to.counted = True

            # store the trackable object in our dictionary
            trackableObjects[objectID] = to

        # update counter in top left
        # textsurface = myfont.render(str(ct.get_count()), False, (0, 0, 0))
        # if total_up != total_up_old or total_down != total_down_old:
        textsurface1 = myfont.render("IN: "+str(total_up), False, (255, 255, 255))
        textsurface2 = myfont.render('OUT: '+str(total_down), False, (255, 255, 255))
        lcd.blit(textsurface1,(0,0))
        lcd.blit(textsurface2,(0,25))

        total_up_old = total_up
        total_down_old = total_down

        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                print('terminating...')
                screencap = False
                break

        # for running the save on for a certain amount of time
        # if time.time() - start_time >= 10:
        #    print('terminating...')
        #    screencap = False

        # empty mode_list every AMBIENT_TIME seconds
        if len(mode_list) > AMBIENT_TIME:
            mode_list = []
        time.sleep(max(1./25 - (time.time() - start), 0))

    # Release everything if job is finished
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
