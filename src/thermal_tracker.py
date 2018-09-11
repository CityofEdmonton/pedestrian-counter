from Adafruit_AMG88xx import Adafruit_AMG88xx
import pygame
import os
import math
import time
import numpy as np
from scipy.interpolate import griddata
import cv2
from colour import Color
from ThermalCamera import ThermalCamera
from CentroidTracker import CentroidTracker

from multiprocessing import Process, active_children
import pexpect

#The preferred # of frames per second.
FPS = 10

#MINTEMP = 26
#MAXTEMP = 30

#how many color values we can have
COLORDEPTH = 1024

# For headless pygame
os.putenv('SDL_VIDEODRIVER', 'dummy')

# For displaying pygame
#os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()

#initialize the sensor
sensor = ThermalCamera()

points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]

#sensor is an 8x8 grid so lets do a square
height = 240
width = 240

#the list of colors we can choose from
blue = Color("indigo")
detectionColor = Color("red")
colors = list(blue.range_to(Color("red"), COLORDEPTH))

#create the array of colors
colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]

displayPixelWidth = width / 30
displayPixelHeight = height / 30

lcd = pygame.display.set_mode((width, height))

lcd.fill((255,0,0))

pygame.display.update()
pygame.mouse.set_visible(False)

lcd.fill((0,0,0))
pygame.display.update()

#TODO: Remove me
# Prepare the OpenCV blob detector. For now, this only works when saving an image.
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

#initialize centroid tracker
ct = CentroidTracker()

#some utility functions
def constrain(val, min_val, max_val):
  return min(max_val, max(min_val, val))

def map(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

#let the sensor initialize
time.sleep(.1)
frame = 0

#separate process using pexpect to interact with ttn transmission
def transmit(str):
	lora = pexpect.spawn('/home/pi/Projects/opencv-python/src/thethingsnetwork-send-v1')
	while(1):
		# handle all cases
		i = lora.expect(['waiting', 'FAILURE', 'not sending', pexpect.TIMEOUT])
		if i == 0:
			lora.sendline(str)
			print ('PedCount updated!')
		else:
			print ('Lora Failure: retrying...')
			lora.terminate(force=True)
			break

while(True):
	start = time.time()
	#read the pixels
	pixels = sensor.get()
	#print(pixels)

	#perform interpolation
	bicubic = griddata(points, pixels, (grid_x, grid_y), method='cubic')
	#print(bicubic)

	#draw everything
	for ix, row in enumerate(bicubic):
		for jx, pixel in enumerate(row):
			pygame.draw.rect(lcd, colors[constrain(int(pixel), 0, COLORDEPTH- 1)], (displayPixelHeight * ix, displayPixelWidth * jx, displayPixelHeight, displayPixelWidth))
	pygame.display.update()

	surface = pygame.display.get_surface()

	img = pygame.surfarray.array3d(surface)
	img.swapaxes(0,1)


	# Read image
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	img = cv2.bitwise_not(img)

	# Detect blobs.
	keypoints = detector.detect(img)

	for i in range (0, len(keypoints)):
	 	x = keypoints[i].pt[0]
	 	y = keypoints[i].pt[1]

	 	# print little circle
	 	pygame.draw.circle(lcd, (200, 0, 0), (int(x), int(y)), 7, 3)
		
	# update  our centroid tracker using the detected centroids
	objects = ct.update(keypoints)

	pygame.display.update()
	
	frame += 1
	time.sleep(max(1./25 - (time.time() - start), 0))

	# transmit pedcount data every 100 frames
	if frame == 1 or frame % 100 == 0:
		# end current lora processes
		plist = active_children()
		for p in plist:
			if p.name == 'lora_proc':
				p.terminate()
		loraproc = Process(target=transmit,  name='lora_proc', args = (str(ct.get_count()),))
		loraproc.start()
	
#	print("Person Count:")
	print(ct.get_count())

print("terminating...")
