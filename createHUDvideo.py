#!/usr/bin/env python3

import os
import sys
import cv2
import numpy as np

# If True - no interpolation - one frame per data point - not real time
HIGH_SPEED = False

# Define the speedometer angle/MPH
## 0 -> 170 degrees = 0MPH to 50MPH, angle = numerator / (input MPH)
ANGLE_SPEEDOMETER = 17.0/5.0
## 0 -> 170 degrees = 0FT to 2500FT, angle = numerator / (input FT)
ANGLE_ALTIMETER = 17.0/250.0

# Pixels moved from center of image to center of travel for indicator
SPEEDOMETER_X_OFFSET = -66
SPEEDOMETER_Y_OFFSET = 3
ALTIMETER_X_OFFSET = 75
ALTIMETER_Y_OFFSET = 3

def printUsageAndQuit(progName):
    print('USAGE:  {} <your_mission_file.gpx> <framerate: [24, 30, or 60]>, <left_foreground.png> <right_foreground.png> <background.png> <output_filename.avi> <[optional] altitude offset for barometer drift>'.format(progName))
    quit()

class HUDVideo:

    # class variables
    gpxFilename = ''
    framerate = 0
    left_indicator_img = ''
    right_indicator_img = ''
    background_img = ''
    videoFilename = ''
    frameSize = ()
    numPoints = 0
    imageCreator = None
    high_speed = HIGH_SPEED
    altitude_offset = 0

    def __init__(self, filename, framerate, left_indicator_img, right_indicator_img, background_img, videoFilename, altitude_offset):
        '''
        Prep variables and stuff to make the video
        '''
        self.gpxFilename = filename
        self.framerate = framerate
        self.left_indicator_img = left_indicator_img
        self.right_indicator_img = right_indicator_img
        self.background_img = background_img
        self.videoFilename = videoFilename
        self.frameSize = (0,0)
        self.elapsed_time = 0.0
        self.altitude_offset = altitude_offset

    def start(self):
        from imageCreator import getFrameSize, ImageCreator

        # Query frameSize for input images
        self.frameSize = getFrameSize(self.background_img)
        left_offset = (SPEEDOMETER_X_OFFSET, SPEEDOMETER_Y_OFFSET)
        right_offset = (ALTIMETER_X_OFFSET, ALTIMETER_Y_OFFSET)
        self.imageCreator = ImageCreator(self.left_indicator_img, left_offset,
                                         self.right_indicator_img, right_offset , self.background_img)

        print('  GPX filename: {}'.format(self.gpxFilename))
        print('  Altitude offset: {}'.format(self.altitude_offset))
        print('  Output video filename: {}'.format(self.videoFilename))
        print('  video dimensions: {} X {}'.format(self.frameSize[0], self.frameSize[1]))
        print('  framerate: {}fps'.format(self.framerate))
        print('  left foreground: {}'.format(self.left_indicator_img))
        print('  right foreground: {}'.format(self.right_indicator_img))
        print('  background: {}'.format(self.background_img))
        if self.high_speed:
            print('  ! High speed video playback enabled - one frame per datapoint - no fill frames !')
        print('  ------------------------------------------\n')

        from gpx_file_parser import load_data
        #from pandas import DataFrame
        data = load_data(self.gpxFilename)
        if not data[0]:
            print('ERROR: gpx_file_parser.load_data returned a failure')
            quit()
        # Grab the pandas.DataFrame object
        df = data[1]
        self.numPoints = len(df)
        self.elapsed_time = (df['Time'][len(df)-1] - df['Time'][0]).total_seconds()

        print('Number of points in {}:  {}'.format(self.gpxFilename, self.numPoints))
        print('Min speed:       %.2f MPH' % (df['Speed'].min()))
        print('Max speed:       %.2f MPH' % (df['Speed'].max()))
        if self.altitude_offset != 0:
            print('Altitude offset selected: %.2f Feet' % self.altitude_offset)
            print('Min altitude (raw data):    %.2f Feet' % (df['Altitude'].min()))
            print('Max altitude (raw data):    %.2f Feet' % (df['Altitude'].max()))
            print('Min altitude (offset):    %.2f Feet' % (df['Altitude'].min() + self.altitude_offset))
            print('Max altitude (offset):    %.2f Feet' % (df['Altitude'].max() + self.altitude_offset))
        else:
            print('Min altitude:    %.2f Feet' % (df['Altitude'].min()))
            print('Max altitude:    %.2f Feet' % (df['Altitude'].max()))
        print('Min temperature: %.2f F' % (df['Temperature'].min()))
        print('Max temperature: %.2f F' % (df['Temperature'].max()))
        print('Total distance:  %.2f Miles' % (df['Distance'].max()))
        print('Start time:      {}'.format(df['Time'][0].strftime('%Y-%m-%d  @ %H:%M:%S')))
        print('End time:        {}'.format(df['Time'][len(df)-1].strftime('%Y-%m-%d  @ %H:%M:%S')))
        print('Elapsed:         {} seconds'.format(self.elapsed_time))

        x_axis = []
        for i in range(len(df)):
            x_axis.append( (df['Time'][i] - df['Time'][0]).total_seconds() )

        # Generate spline data for speed and altitude
        #from scipy.interpolate import CubicSpline
        # PCHIP 1-d monotonic cubic interpolation
        from scipy.interpolate import PchipInterpolator
        import matplotlib.pyplot as plt

        # Apply altitude offset to data - clip at zero feet
        for i in range(len(df['Altitude'])):
            df.loc[i, 'Altitude'] = max(0, df['Altitude'][i] + self.altitude_offset)
        # Clip speed to 0 MPH
        for i in range(len(df['Speed'])):
            df.loc[i, 'Speed'] = max(0, df['Speed'][i])

        # Prep plot parameters
        plt.figure(figsize = (6.5, 4))
        x_sample_rate = 1.0 / self.framerate
        x_tick_interval = np.arange(0, self.elapsed_time, x_sample_rate)

        # Create interpolated spline data
        #cs_speed = CubicSpline(x_axis, df['Speed'])
        #cs_altitude = CubicSpline(x_axis, df['Altitude'])
        cs_speed = PchipInterpolator(x_axis, df['Speed'])
        cs_altitude = PchipInterpolator(x_axis, df['Altitude'])

        # Pull out the array of data points
        cs_speed_array = cs_speed(x_tick_interval)
        cs_altitude_array = cs_altitude(x_tick_interval)

        # Clip spline data points
        for i in range(len(cs_speed_array)):
            cs_speed_array[i] = max(0, cs_speed_array[i])
            cs_altitude_array[i] = max(0, cs_altitude_array[i])

        plt.plot(x_axis, df['Speed'], 'o', label='gpx_speed')
        plt.plot(x_axis, df['Altitude'], 'o', label='gpx_altitude')

        plt.plot(x_tick_interval, cs_speed_array, label='speed')
        plt.plot(x_tick_interval, cs_altitude_array, label='altitude')
        plt.legend(loc='lower left', ncol=1)
        plt.show()



        if self.high_speed:
            num_points = self.numPoints
            y_axis_speed = df['Speed']
            y_axis_altitude = df['Altitude']
        else:
            num_points = len(cs_speed_array)
            y_axis_speed = cs_speed_array
            y_axis_altitude = cs_altitude_array

        print('Created a video with {} frames at a framerate of {}fps'.format(num_points, self.framerate))
        proceed = input('Process video? (Y/N):')
        if proceed.upper() != 'Y':
            quit()

        # Prep video writer
        #vidOut = cv2.VideoWriter(self.videoFilename, cv2.VideoWriter_fourcc(*'DIVX'), self.framerate, self.frameSize)
        #vidOut = cv2.VideoWriter(self.videoFilename, cv2.VideoWriter_fourcc(*'H264'), self.framerate, self.frameSize)
        vidOut = cv2.VideoWriter(self.videoFilename, cv2.VideoWriter_fourcc(*'MP4V'), self.framerate, self.frameSize)
        #vidOut = cv2.VideoWriter(self.videoFilename, cv2.VideoWriter_fourcc(*'FFV1'), self.framerate, self.frameSize)

        for i in range(num_points):
            angle_speedometer = y_axis_speed[i] * ANGLE_SPEEDOMETER
            angle_altimeter = y_axis_altitude[i] * ANGLE_ALTIMETER

            image = self.imageCreator.createImage(angle_speedometer, angle_altimeter)
            # convert to 8-bit image to accomodate VideoWriter.write()
            #image = (image*255).astype(np.uint8)
            image = image.astype(np.uint8)
            '''cv2.imshow('img', image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            quit()'''
            if  0 == ((i+1) % int(num_points / 100)):
                print('%.2f%% complete' % ((100.0) * ((i+1)/ float(num_points))))

            vidOut.write(image)

        vidOut.release()
        print('Finished')

if (__name__ == '__main__' ):

    altitude_offset = 0

    if len(sys.argv) != 7 and len(sys.argv) != 8:
        printUsageAndQuit(sys.argv[0])
    else:
        # verify input parameters
        try:
            filename = sys.argv[1]
            framerate = int(sys.argv[2])
            left_indicator_img = sys.argv[3]
            right_indicator_img = sys.argv[4]
            background_img = sys.argv[5]
            videoFilename = sys.argv[6]
            if 8 == len(sys.argv):
                altitude_offset = int(sys.argv[7])
        except:
            printUsageAndQuit(sys.argv[0])
        if 24 != framerate and 30 != framerate and 60 != framerate:
            printUsageAndQuit(sys.argv[0])

        if not os.path.exists(filename) or not os.path.exists(right_indicator_img) \
            or not os.path.exists(left_indicator_img) or not os.path.exists(background_img) \
            or not right_indicator_img.endswith('.png') or not background_img.endswith('.png'):
            printUsageAndQuit(sys.argv[0])

        foo = HUDVideo(filename, framerate, left_indicator_img, right_indicator_img, background_img, videoFilename, altitude_offset)
        foo.start()
