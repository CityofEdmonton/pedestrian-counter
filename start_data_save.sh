#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"


if [ -z "$1" ]; then
    echo "Pass virtual env directory as argument"
else
    echo "Activating the virtual python environment"
    source $DIR/$1/bin/activate #ped-detector is the name of your virtual env
    echo "Running the pedestrian detector"
    if [ "$2" == "--headless" ]; then
        python $DIR/src/thermal_save.py --headless 256
    else 
        python $DIR/src/thermal_save.py 256
    fi
fi



