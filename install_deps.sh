#!/bin/bash

OPENCV_VERSION='4.1.1'    # Version to be installed
# OPENCV_CONTRIB='NO'       # Install OpenCV's extra modules

sudo apt-get -y update
sudo apt-get -y upgrade       # Uncomment to install new versions of packages currently installed
sudo apt-get -y autoremove    # Uncomment to remove packages that are now no longer needed

sudo apt-get install -y build-essential cmake

# GUI (if you want GTK, change 'qt5-default' to 'libgtkglext1-dev' and remove '-DWITH_QT=ON'):
sudo apt-get install -y qt5-default libvtk6-dev

sudo apt-get install -y zlib1g-dev libjpeg-dev libwebp-dev libpng-dev libtiff5-dev libjasper-dev \
                        libopenexr-dev libgdal-dev

sudo apt-get install -y libdc1394-22-dev libavcodec-dev libavformat-dev libswscale-dev \
                        libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev yasm \
                        libopencore-amrnb-dev libopencore-amrwb-dev libv4l-dev libxine2-dev

sudo apt-get install -y libtbb-dev libeigen3-dev

sudo apt-get install -y python-dev python-tk python-numpy python3-dev python3-tk python3-numpy

sudo apt-get install -y ant default-jdk

sudo apt-get install -y doxygen

# Get, make and install opencv
sudo apt-get install -y unzip wget
wget https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip
unzip ${OPENCV_VERSION}.zip && rm ${OPENCV_VERSION}.zip
mv opencv-${OPENCV_VERSION} OpenCV
cd OpenCV && mkdir build && cd build
cmake -DWITH_QT=ON -DWITH_OPENGL=ON -DFORCE_VTK=ON -DWITH_TBB=ON -DWITH_GDAL=ON \
      -DWITH_XINE=ON -DBUILD_EXAMPLES=ON -DENABLE_PRECOMPILED_HEADERS=OFF ..
make -j4
sudo make install
sudo ldconfig

# Install other dependencies
sudo pip install numpy
sudo pip install gpxpg
sudo pip install pandas
sudo pip3 install matplotlib
