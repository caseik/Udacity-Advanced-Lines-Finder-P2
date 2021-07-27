import cv2
import os
import numpy as np
import matplotlib.image as mpimg

class Camera:

    def __init__(self):
        self.calibrated = False
        self.mtx = None
        self.dist = None
        self.fps = 0
        self.width = 0
        self.height = 0


    def load_video(self,input_path=""):
        cap = cv2.VideoCapture(input_path)
        video = []
        if (cap.isOpened()== False):
            raise Exception("Error opening video stream or file")
        while(cap.isOpened()):
            ret,frame=cap.read()
            if ret == True:

                video.append(frame)

            else:
                break
        self.fps = int(cap.get(5))
        self.height = int(cap.get(4))
        self.width = int(cap.get(3))
        cap.release()
        return video

    def load_image(self,input_path=""):
        img = cv2.imread(input_path)
        return img


    def load_images_in_folder(self,input_path=""):
        images=[]
        for image_name in os.listdir(input_path):
            image=self.load_image(os.path.join(input_path,image_name))
            images.append(image)

        return images
    def load_videos_in_folder(self,input_path=""):
        videos=[]
        for video_name in os.listdir(input_path):
            video=self.load_video(os.path.join(input_path,video_name))
            videos.append(video)

        return videos

    def undistort_video(self,video=[]):

        if self.calibrated == False:
            raise Exception("Error, camera was not calibrated")
        undist_video=[]
        if (video== []):
            raise Exception("Error opening video")
        for img in video:
            img=self.undistort_image(img)
            undist_video.append(img)

        return undist_video


    def undistort_image(self,img= []):
        if self.calibrated == False:
            raise Exception("Error, camera was not calibrated")
        img = cv2.undistort(img, self.mtx, self.dist, None, self.mtx)
        return img

    def save_video(self,video=[],output_path='output/video/',video_name='video',FPS=25):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path+video_name,fourcc, self.fps, (self.width,self.height))


        for img in video:
            out.write(img)

        out.release()

    def save_image(self,image=[],output_path="'output/images",image_name="image"):
        cv2.imwrite(os.path.join(output_path , image_name),  image)

    def calibrate_camera(self,horizontal_corners=9,vertical_corners=6,input_path='camera_cal/'):
        img_points = []
        objective_points = []
        img=[]
        for img_name in os.listdir(input_path):
            img = mpimg.imread(os.path.join(input_path,img_name))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            ret, corners = cv2.findChessboardCorners(gray, (horizontal_corners, vertical_corners), None)
            if ret == True:
                img_points.append(corners)
                obj_points = np.zeros((vertical_corners*horizontal_corners, 3),np.float32)
                obj_points[:,:2] = np.mgrid[0:horizontal_corners,0:vertical_corners].T.reshape(-1,2)
                objective_points.append(obj_points)
            else:
                print(img_name + " discarded for camera calibration")
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objective_points, img_points, (img.shape[1],img.shape[0]), None, None)
        self.mtx = mtx
        self.dist = dist
        self.calibrated = True

    def DEBUG_draw_corners(self,horizontal_corners=9,vertical_corners=6,output_path='output/draw_corners/',input_path='camera_cal/'):

        for img_name in os.listdir(input_path):
            img = mpimg.imread(os.path.join(input_path,img_name))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            ret, corners = cv2.findChessboardCorners(gray, (horizontal_corners, vertical_corners), None)
            if ret == True:
                cv2.drawChessboardCorners(img, (horizontal_corners, vertical_corners), corners, ret)
                cv2.imwrite(os.path.join(output_path , img_name),  img)
            else:
                print(" It not possible to draw the corners in:" + img_name)

    def DEBUG_draw_undistort_images(self,input_path='camera_cal',output_path='output_images/cal_images'):
        if self.calibrated == False:
            raise Exception("Error, camera was not calibrated")

        if not os.path.isdir(output_path):
            raise Exception("Error output path does not exist in draw_undistort_images")


        for img_name in os.listdir(input_path):
            img = mpimg.imread(os.path.join("camera_cal/",img_name))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            dst = cv2.undistort(gray, self.mtx, self.dist, None, self.mtx)
            result = np.concatenate((gray, dst),axis=1)
            cv2.imwrite(os.path.join(output_path,img_name),result)


