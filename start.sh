#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

echo "Activating the virtual python environment"
source $DIR/ped-detector/bin/activate #ped-detector is the name of your virtual env


echo "Running the pedestrian detector"
python $DIR/src/thermal_tracker.py

