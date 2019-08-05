# animatedHUD
Video creator for adding a HUD to paragliding videos for YouTube  
  
# Example on YouTube
[![](http://img.youtube.com/vi/Kk9YNb6YHbY/0.jpg)](http://www.youtube.com/watch?v=Kk9YNb6YHbY "Say Hello to My Little Pickle")  
  
# Install Dependencies
This script was designed on an Ubuntu 64-bit machine. It has been verified to work on versions as old as 16.04 and as new as 18.04. You may have to modify the installation script if it happens to fail - although those changes should be minimal. It likely will "just work".  
  
You will need to install dependencies prior to running the script. Do this with:  
``` python
./install_deps.sh
```

# Video Creation
After installation, you may create a heads-up display (HUD) video by running the following command:  
``` python
./createHUDvideo.py test.gpx 30 pickle_rick_left_arm.png pickle_rick_right_arm.png pickle_rick_50MPH_2500FT.png outputVid.mp4 82
```

## Argument Description
The script takes arguments and order matters. No effort was taken to make this particularly nice for you, so you'll have to deal.  
**1st argument**:  Input GPX file  
**2nd argument**:  Desired output video framerate.  Only 24, 30, and 60FPS are valid. If you want to do something weird, remove the check on your input  
**3rd argument**:  Filename for the "left" indicator image. This can be the same as the "right" if you want. I'm making a cartoon, so each are unique.  
**4th argument**:  Filename for the "right" indicator image.  
**5th argument**:  Filename for the static base image - the body, or the dial or whatever.  
**6th argument**:  Filename of the video to be created. (It's internally set to produce an MP4, but you can change that too)  
**7th (optional) argument**:  An offset to be applied to the altitude values found in the GPX file. The test.gpx file has a lowest altitude of -82ft, so I set this to positive 82 to bring up the floor of the altitude range. This is useful when the GPS logger altimeter was not initially calibrated well prior to starting.  
  
# DEBUG - fast video output
By default, the script uses the PCHIP 1-d monotonic cubic interpolator from the scipy.interpolate.PchipInterpolator library to calculate what values would be between the data points recorded in the GPX file and create a video stream that matches realtime. The GPX file may only record one data point per second or so and it may actually vary based on the amount of activity sensed.  
  
To bypass this scheme and just record one frame of video per data point recorded, change the "**HIGH_SPEED = False**" to **True** on *Line 9* of the **createHUDvideo.py** script.  This will very quickly produce an output video for you, but it will be unusable as a HUD because it is no longer realtime. It is useful to verify that the script and your machine have all the dependencies needed to create high quality videos when you're ready.  The script may takes a few hours to create a video for you. This sucks, but I don't care.  
