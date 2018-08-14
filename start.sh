#!/bin/bash
echo "Activating the virtual python environment"
source ./ped-detector/bin/activate
echo "Running the pedestrian detector"
python ./src/thermal_tracker.py