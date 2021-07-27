# **Advanced Lane Finding** 
[//]: # (Image References)

[image1]: ./gui_sample.jpg "gui_sample"  
[image2]: ./output/draw_corners/calibration2.jpg "calibration2"
[image3]: ./output/draw_corners/calibration7.jpg "calibration7"
[image4]: ./output/draw_corners/calibration17.jpg "calibration17"
[image5]: ./output/cal_images/calibration2.jpg "calibration2"
[image6]: ./output/cal_images/calibration3.jpg "calibration7"
[image7]: ./output/cal_images/calibration4.jpg "calibration17"
---
## **Introduction** 

For this project I created a GUI to make easier to find the right parameters for the videos or the images.

![alt text][image1]
I organized most of the code in classes.

The first class is the camera class, it manages all the things related with video/image I/O.
The methods have self-explanatory names:

```
def load_video
def load_image
def load_videos_in_folder
def load_images_in_folder
def undistort_video
def undistort_image
def save_video
def save_image
def calibrate_camera
def DEBUG_draw_corners
def DEBUG_draw_undistort_images
```
The second class is image_editor, and have the follow methods:

```
def __thresh_lum
def __thresh_sat
def __thresh_gradx
def __thresh_grady
def __thresh_mag
def __thresh_dir
def combinator_gradients
def combinator_colors
def gradient_and_color 
def resize_image
def image2gui  (Prepare the image to be displayed in the GUI)
def select_points (Select the points to make the perspective transformation)
def perspective
```

The third class is the LineFinder with these methods

```
def __center_calculation
def __radius_calculation
def __look_ahead
def __find_lane_pixels
def __sanity_check
def fit_polynomial
def draw_lines
```

And the last class is the Line class to track lines features
```
def avg_fits (average of polynomial fits to smooth the image)
```
The GUI is one single script that uses these classes.

## **Camera calibration** 

The first statement  required by the rubric is camera calibration.
It was addressed in the camera class, with the method calibrate_camera.
Just following the procedure that was taught in the course using findChessboardCorners and then calibrateCamera.
In the GUI I added a button to automatically save all debugging pictures of camera calibration.

The methods related to camera calibration are:
```
def calibrate_camera
def DEBUG_draw_corners
def DEBUG_draw_undistort_images
```
They are inside camera.py

Here some pictures with the results:


![alt text-1][image2 ] ![alt text-2][image3]![alt text-3][image4] 

And here some example of the calibration result:

![alt text-][image5] ![alt text-2][image6]![alt text-3][image7] 

Some calibration images were discarded because they don't have enough corners.

 ```
calibration5.jpg discarded for camera calibration
calibration1.jpg discarded for camera calibration
calibration4.jpg discarded for camera calibration
 ```

## **Pipeline**

### Undistord images

We start the pipeline with distortion-correction. With the parameters mtx and dist obtained during camera calibration, we can undistord images using the method:  ``` def undistort_image```.

This was added in the GUI as a button so we can see how the distortion-correction affects to the image in real time or even in a video:

 ![ alt-text-1](./gifs/undistord.gif "undistor" )

### Color transforms and gradients

All methods related to color and gradient transformation are inside image_editor.py, and these methods are used in the GUI script.

``` 
def __thresh_lum
def __thresh_sat
def __thresh_gradx
def __thresh_grady
def __thresh_mag
def __thresh_dir
def combinator_gradients
def combinator_colors
def gradient_and_color 
```

In this project I only used color transformation in HLS color space and gradient filters, these filters are combined with a function that was suggested in the course, all filters can be turned on or off independently.

For the gradients

 ``` 
 (GradX AND Grady) OR (Mag_binary AND Dir_binary)  
 ``` 

And for the colors:

 ```
Sat AND Lum 
 ```

 A better idea will be to program a fully configurable RGB, HSV, HSL and gradient methods were you can combine all this methods with arbitrary logical functions, but this was not implemented.

 Although you can intuitively know the effects that the filters will produce in the image. When we combine all these filters, I think the best option is to have a visual output to see the effects in real time.

 Here some example of the program while tuning the parameters. The second screen has 4 modes: Normal, Gradient, Color or Both, so you can choose which filters you want to see:

![ alt-text-1](./gifs/colors_and_gradients.gif "colgra" )

### Perspective transform

Perspective transform is addressed also in image_editor.py with the methods:

```
def select_points
def perspective
```

It is also performed with the GUI , we can see the result of the transformation in the lower right panel.
There is button in the GUI with the label "Perspective Transform", when clicked, a window will popup.

This window will contain the last frame displayed. In this image you can select 4 points for the transformation, the  destination points are the corners of the image. One problem is that the points need to be select in a specific order: lower left, high left, high right and lower right. This is could be corrected but since I am the only user of this program  its a minor inconvenience.

To perform this I used the graphical input function in matplotlib  https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.ginput.html

Once you select the points the result will be displayed (Unfortunately, the popup window can not be capture with the built-in program of windows to record screen, sorry.):

![ alt-text-1](./gifs/perspective_transform.gif "persp" )

### Lane-line pixels and fit their positions with a polynomial

Finding Lane line pixels is performed in LineFinder, with the methods

``` 
def __find_lane_pixels
def fit_polynomial
``` 

The method is equal to the one taught in the course. We use a set of windows that will try to fit the lines but searching a good enough amount of pixels. If the quantity is enough, we move the next window to the mean position of these pixels, trying to match the lines. Later, with this boxes with pixels, we try to fit a second order polynomial to match the curve with the function ```np.polyfit()```. This process is not configurable inside the GUI, although some parameters could improve or deteriorate the performance, like nº windows, margins and other parameters related with sanity checks. In the GUI there is a button (Show result) that should be clicked when we are confident that the filters and perspective transform are good enough (other wise the program could crash...):

![ alt-text-1](./gifs/line_finder.gif "linefinder" )

Also take in to account that the gifs displayed is using the look head function, this function do not move the windows when we are confident we are on the right track, and some smoothing is applied also.

The sanity checks can be found searching were the variable ``` self.sanity =False ```  appears.

The sanity check will fail (deactivating the look a head filter for that frame) when:

The two curvatures have a huge difference

``` 
np.abs(LineL.radius_of_curvature-LineR.radius_of_curvature)>1000: 
```
The mean of the curvature is too large
``` 
 if  self.radius_of_curvature >10000:
            self.sanity =False
``` 
When lines can't be found
``` 
try:
        left_fit = np.polyfit(lefty, leftx,2)
        right_fit = np.polyfit(righty,rightx,2)
except Exception:
        print("Can not find the Lane!!!")
        self.sanity =False
        return img
``` 
And when not enough pixels can't be found:

``` 
if minpix > len(good_left_inds):
        self.sanity =False

if minpix > len(good_right_inds):
        self.sanity =False
``` 



### Radius of curvature and the position of the vehicle with respect to center

This was performed also in LineFinder class.


``` 
def __radius_calculation(self,img,leftx,rightx,lefty,righty):

        ym_per_pix = 30/720 
        xm_per_pix = 3.7/700 

        left_fit_cr = np.polyfit(lefty*ym_per_pix, leftx*xm_per_pix,2)
        right_fit_cr = np.polyfit(righty*ym_per_pix, rightx*xm_per_pix,2)
        ploty = np.linspace(0, img.shape[0]-1, img.shape[0] )

        y_eval = np.max(ploty*ym_per_pix):
      
        f1l = (2*left_fit_cr[0]*y_eval+left_fit_cr[1])
        f1r = (2*right_fit_cr[0]*y_eval+right_fit_cr[1])
        numerador_l =(1+f1l**2)**1.5
        numerador_r =(1+f1r**2)**1.5
        f2l = 2*left_fit_cr[0]
        f2r = 2*right_fit_cr[0]
        left_curverad = numerador_l/np.absolute(f2l)  
        right_curverad = numerador_r/np.absolute(f2r) 
    
        return left_curverad, right_curverad
``` 

I simply performed the steps indicated in the course. With the detected pixels we fit a polynomial of second order but with the data in the metric space, and not in pixel space. Them we calculate the curvature radio of this polynomial and finally, with the radio of curvature of both lines, we compute the  radio curvature as the average of both  

```
self.radius_of_curvature = (LineL.radius_of_curvature  + LineR.radius_of_curvature)/2
```

in this LineFinder function (that also draw the final image):


```
def draw_lines(self,img,img_ori,LineL,LineR,Minv):
```

For the center calculation I perform this operation:

``` 
def __center_calculation(self,img,left_fitx,right_fitx):
        xm_per_pix = 3.7/700 
        lane_center = (left_fitx[-1] + right_fitx[-1])//2
        car_center = img.shape[1]/2  
        self.center_offset = (lane_center - car_center) * xm_per_pix
``` 

### Result in images

## Discussion

For this project I though more in learn how to build a tool for solving this type of problems more than in actually solve the problem perfectly. Although the program has some considerable bugs, and a horrible performance.  I think it serves its purpose, I think a good result was achieved for all the test images and videos with the exception of the harder challenge video. Sometimes there was a problem with the radius of curvature, in spite there was some curvature in the real line,  the polyfits function fitted a straight line, making the radius of curvature to blow up.

Also I  think realized a  fundamental problem while doing this project, its my intuition (let me know if I am wrong) that we can always find a video or an image in which the lines can not be detected for any given parameters. This is an important problem taking in to account that this is for a self driving car. Maybe in a controlled environments this is not a problem, but in the wilde we can find a lot of horrible roads, weather conditions or lighting situations that make this complicated. Its true that in a real life project we can use the finest quality cameras and better methods that I might don't know, but its is clear for me now why deep learning was suggested at the end of the section.

I think there is a trade off. These techniques are explainable, and we can control them. We know how they work and when they work (something incredible useful), but this make them very inflexible. Deep learning is more flexible, I saw that can make an incredible job, but its lack of explicability (kind of black box once its working) would make me uncomfortable  when  deploying this in a real product, because there are not 100% guarantees. On the contrary with the computer vision techniques taught in the course I think we can guaranteed a result under certain conditions and it's incredible powerful for many situations.

 An improvement that I might do its to re-implement the program in C++ and add one streaming framework, to being able to perform all this operations in a streaming video from youtube for example, instead of having to load all the video inside the program, also It would be easier to control the fps rate or implement the rewind or fast forward options, to make more easy the analysis. Another drawback is the lack of more options like RGB space color that will have been certainly beneficial.

