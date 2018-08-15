#!/bin/bash
echo "Activating the virtual python environment"
source /home/pi/Projects/opencv-python/ped-detector/bin/activate
echo "Running the pedestrian detector"
python /home/pi/Projects/opencv-python/src/thermal_tracker.py

