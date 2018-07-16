# opencv-python
An example OpenCV Python app.

## Deploying

TODO

## Contributing

Setting up the development environment for working with ped-counter requires multiple dependencies.

Run the following in a shell to install them:

``` bash
sudo apt-get update
sudo apt-get install python-opencv
sudo apt-get install python-matplotlib
sudo apt-get install python-gi python-gi-cairo python3-gi python3-gi-cairo gir1.2-gtk-3.0
sudo apt-get install libqtgui4


```

### For OpenCV's dependencies
``` bash
sudo apt-get install build-essential cmake pkg-config
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install libxvidcore-dev libx264-dev
sudo apt-get install libgtk2.0-dev libgtk-3-dev
sudo apt-get install libatlas-base-dev gfortran
```

### For compiling python bindings
``` bash
sudo apt-get install python2.7-dev python3-dev
```

### For compiling OpenCV from source
``` bash
cd ~
wget -O opencv.zip https://github.com/opencv/opencv/archive/3.4.2.zip
unzip opencv.zip
```

After extracting the Open CV source, we need to create a new Python3 environment.
``` bash
virtualenv -p python3 opencv-env 
source opencv-env/bin/activate  
```

Ensure you are using the new opencv-env environment and switch to the OpenCV source directory.
``` bash
cd ~/opencv-3.4.2/
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D BUILD_EXAMPLES=ON ..
```

The guide referenced in this wiki mentions something important: ensure the output of the last command makes sense. Specifically, ensure cmake knows where your python interpreter is.

{INSERT PYTHON CLI IMAGE HERE}

Open /etc/dphys-swapfile and increase the CONF_SWAPSIZE to 1024.

Then, restart the service:
``` bash
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
```

Finally, we're ready to compile Open CV for our environment. This takes ~1.5 hours.
``` bash
make -j4
```

### Installing OpenCV
https://www.pyimagesearch.com/2017/09/04/raspbian-stretch-install-opencv-3-python-on-your-raspberry-pi/
In the future, also build opencv-contrib from source?
https://github.com/opencv/opencv_contrib
