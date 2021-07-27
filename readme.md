# **CarND-Advanced-Lane-Lines** 
[image1]: ./gui_sample.jpg "gui_sample"  
[image2]: ./Sample_gui2.JPG "gui_sample2"  

[image3]: ./output/images/result1.jpg "result1"  
[image4]: ./output/images/result6.jpg "result7"  
 

## Description

For this project I made a GUI to find the parameters that better find the lines in a video or picture.

![alt text][image1]


## Getting Started

![alt text][image2]

Once you run the program you have different options.

You can load videos that are in the folder test_videos or pictures in the folder test_images.

Then before start editing you should select a data folder to save or load parameters that will process the images.

Once you had selected, you can use the editor to find the lines.

The camera calibration button will calibrate the camera with calibration pictures inside the folder camera_cal.

You can save debug images for this calibration with button  Save Debug Images

Once you have found the right parameters you can see the results by clicking "Show results" and save the parameters with the button save data in the folder you have chosen.

Then if you want to save the video or images result, you must load the data that you have saved by clicking Load data, then click in show result, and lastly click in save video/images (WARNING: For videos this is performed in a very inefficient way, so the program can take a long time to save the videos)

Some results obtained with this program (The different results can be found also in the output folder):

![alt text][image3]
![alt text][image4]

![ alt-text-1](./gifs/videoresult.gif "v1" )

### Dependencies

This repositories contains the videos and the images output. The videos were converted to .avi for compatibility with python-opencv.

```
sudo apt-get update
sudo apt-get upgrade
sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0
```

### Installing

In Ubuntu, then inside a virtualenv

```
pip3 install -r requiremetns.txt
```

### Executing


```
python3 pipeline_gui.py
```
