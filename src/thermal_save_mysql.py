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
import RPi.GPIO as GPIO
from dragino import Dragino
import logging
from trackableobject import TrackableObject
import mysql.connector
from pytz import timezone
# some utility functions


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def mysql_save_insert(mysql_config, list):
    sqlDate = datetime.now(timezone('MST')).strftime('%Y-%m-%d %H:%M:%S')
    conn = mysql.connector.connect(
        host=mysql_config["host"],
        user=mysql_config["user"],
        passwd=mysql_config["passwd"],
        database=mysql_config["database"]
    )
    cursor = conn.cursor()
    sql = "INSERT INTO ped_count (count, device_id, description, time_stamp, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (payload['c'], mysql_config["device_id"],
           mysql_config["description"], sqlDate, payload['a'], payload['o'])
    try:
        cursor.execute(sql, val)
        conn.commit()
        print("inserted values %s"%(str(val)))
    except MySQLdb.IntegrityError:
        print("failed to insert values %s"%(str(val)))
    finally:
        cursor.close()
        conn.close()


def send_mysql(delay):
    global payload
    with open("mysql_config.json") as f:
        mysql_config = json.load(f)
    while True:
        for child in active_children():
            if child.name == 'mysql_proc':
                child.terminate()
        
        proc = Process(
            target=mysql_save_insert, name='mysql_proc', args=(mysql_config, payload, ))
        proc.start()
        time.sleep(delay)


def count_within_range(list1, l, r):
    '''
    Helper function to count how many numbers in list1 falls into range [l,r]
    '''
    c = 0
    # traverse in the list1
    for x in list1:
        # condition check
        if x >= l and x <= r:
            c += 1
    return c


# a - latitude
# o - longitude
# c - count
payload = {'a': 53.539738, 'o': -113.489795, 'c': 0}
last_count = 0

def main():
    global payload

    # argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--headless', help='run the pygame headlessly', action='store_true')

    parser.add_argument(
        "--color_depth", help="integer number of colors to use to draw temps", type=int)
    parser.add_argument(
        '--max_temp', help='initial max temperature', type=int)
    parser.add_argument(
        '--ambient_offset', help='value to offset ambient temperature by to get rolling MAXTEMP', type=int)
    parser.add_argument(
        '--ambient_time', help='length of ambient temperature collecting intervals in seconds', type=int)

    parser.add_argument(
        '--blob_min_threshold', help='blod detection min threshold', type=int)
    parser.add_argument(
        '--blob_max_threshold', help='blod detection min threshold', type=int)

    parser.add_argument(
        '--blob_filterbyarea', help='blod detection filter by area', action='store_true')
    parser.add_argument(
        '--blob_min_area', help='blod detection filter by area min area', type=int)

    parser.add_argument(
        '--blob_filterbycircularity', help='blod detection filter by circularity', action='store_true')
    parser.add_argument(
        '--blob_min_circularity', help='blod detection filter by circularity min circularity', type=float)

    parser.add_argument(
        '--blob_filterbyconvexity', help='blod detection filter by convexity', action='store_true')
    parser.add_argument(
        '--blob_min_convexity', help='blod detection filter by convexity min convexity', type=float)

    parser.add_argument(
        '--blob_filterbyinertia', help='blod detection filter by inertia', action='store_true')
    parser.add_argument(
        '--blob_min_inertiaratio', help='blod detection filter by inertia inertia ratio', type=float)

    parser.add_argument(
        '--mysql_send_interval', help='length of intervals between attempted mysql insert in seconds', type=int)

    args = parser.parse_args()
    print(args)
    i2c_bus = busio.I2C(board.SCL, board.SDA)

    COLOR_DEPTH = args.color_depth
    MAX_TEMP = args.max_temp
    AMBIENT_OFFSET = args.ambient_offset
    AMBIENT_TIME = args.ambient_time

    BLOB_MIN_THRESHOLD = args.blob_min_threshold
    BLOB_MAX_THRESHOLD = args.blob_max_threshold

    BLOB_FILTERBYAREA = args.blob_filterbyarea
    BLOB_MIN_AREA = args.blob_min_area

    BLOB_FILTERBYCIRCULARITY = args.blob_filterbycircularity
    BLOB_MIN_CIRCULARITY = args.blob_min_circularity

    BLOB_FILTERBYCONVEXITY = args.blob_filterbyconvexity
    BLOB_MIN_CONVEXITY = args.blob_min_convexity

    BLOB_FILTERBYINERTIA = args.blob_filterbyinertia
    BLOB_MIN_INERTIARATIO = args.blob_min_inertiaratio

    MYSQL_SEND_INTERVAL = args.mysql_send_interval

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
    black = Color("black")
    colors = list(black.range_to(Color("white"), COLOR_DEPTH))

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

    # Change thresholds
    if BLOB_MIN_THRESHOLD:
        params.minThreshold = BLOB_MIN_THRESHOLD
    if BLOB_MAX_THRESHOLD:
        params.maxThreshold = BLOB_MAX_THRESHOLD

    # Filter by Area.
    if BLOB_FILTERBYAREA:
        params.filterByArea = BLOB_FILTERBYAREA
        params.minArea = BLOB_MIN_AREA

    # Filter by Circularity
    if BLOB_FILTERBYCIRCULARITY:
        params.filterByCircularity = BLOB_FILTERBYCIRCULARITY
        params.minCircularity = BLOB_MIN_CIRCULARITY

    # Filter by Convexity
    if BLOB_FILTERBYCONVEXITY:
        params.filterByConvexity = BLOB_FILTERBYCONVEXITY
        params.minConvexity = BLOB_MIN_CONVEXITY

    # Filter by Inertia
    if BLOB_FILTERBYINERTIA:
        params.filterByInertia = BLOB_FILTERBYINERTIA
        params.minInertiaRatio = BLOB_MIN_INERTIARATIO

    # Set up the detector with default parameters.
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

    send_thread = threading.Thread(
        target=send_mysql, args=(MYSQL_SEND_INTERVAL,))
    send_thread.start()

    print('sensor started!')

    while(screencap):
        start = time.time()

        # read the pixels
        pixels = []
        for row in sensor.pixels:
            pixels = pixels + row

        payload['a'] = 0
        payload['o'] = 0
        payload['c'] = ct.get_count_since_last_reading()

        mode_result = stats.mode([round(p) for p in pixels])
        mode_list.append(int(mode_result[0]))

        # instead of taking the ambient temperature over one frame of data take it over a set amount of time
        MAX_TEMP = float(np.mean(mode_list)) + AMBIENT_OFFSET
        pixels = [map_value(p, mode_result[0] + 1, MAX_TEMP, 0,
                            COLOR_DEPTH - 1) for p in pixels]

        # perform interpolation
        bicubic = griddata(points, pixels, (grid_x, grid_y), method='cubic')

        # draw everything
        for ix, row in enumerate(bicubic):
            for jx, pixel in enumerate(row):
                try:
                    pygame.draw.rect(lcd, colors[constrain(int(pixel), 0, COLOR_DEPTH - 1)],
                                     (displayPixelHeight * ix, displayPixelWidth * jx, displayPixelHeight, displayPixelWidth))
                except:
                    print("Caught drawing error")

        surface = pygame.display.get_surface()
        myfont = pygame.font.SysFont("comicsansms", 25)

        img = pygame.surfarray.array3d(surface)
        img = np.swapaxes(img, 0, 1)

        # Read image
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.bitwise_not(img)

        # Detect blobs.
        keypoints = detector.detect(img)
        img_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array(
            []), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        # draw a horizontal line in the center of the frame -- once an
        # object crosses this line we will determine whether they were
        # moving 'up' or 'down'
        pygame.draw.line(lcd, (255, 255, 255),
                         (0, height // 2), (width, height // 2), 2)
        pygame.display.update()

        for i in range(0, len(keypoints)):
            x = keypoints[i].pt[0]
            y = keypoints[i].pt[1]

            # print circle around blobs
            pygame.draw.circle(lcd, (200, 0, 0), (int(
                x), int(y)), round(keypoints[i].size), 2)

        # update our centroid tracker using the detected centroids
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
                    # the historical centroid must present in the lower half of the screen
                    if direction < 0 and centroid[1] < height // 2 and count_within_range(y, height//2, height) > 0:
                        total_up += 1
                        to.counted = True

                    # if the direction is positive (indicating the object
                    # is moving down) AND the centroid is below the
                    # center line, count the object
                    # the historical centroid must present in the upper half of the screen
                    elif direction > 0 and centroid[1] > height // 2 and count_within_range(y, 0, height//2) > 0:
                        total_down += 1
                        to.counted = True

            # store the trackable object in our dictionary
            trackableObjects[objectID] = to

        # update counter in top left
        textsurface1 = myfont.render(
            "IN: "+str(total_up), False, (255, 255, 255))
        textsurface2 = myfont.render(
            'OUT: '+str(total_down), False, (255, 255, 255))
        lcd.blit(textsurface1, (0, 0))
        lcd.blit(textsurface2, (0, 25))

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

        # empty mode_list every AMBIENT_TIME *10 seconds to get current ambient temperature
        if len(mode_list) > AMBIENT_TIME:
            mode_list = []
        time.sleep(max(1./25 - (time.time() - start), 0))

    # Release everything if job is finished
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
