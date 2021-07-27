import cv2
import numpy as np
import matplotlib
matplotlib.use('GTK3Agg')
import matplotlib.pyplot as plt

class ImageEditor:
    def __init__(self):
        self.M = None
        self.Minv = None

    def __thresh_lum(self,img=[],thresh=(0,255)):
        hls = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
        l_channel = hls[:,:,1]
        l_binary = np.zeros_like(l_channel)
        l_binary[(l_channel >= thresh[0]) & (l_channel <= thresh[1])] = 1

        return l_binary

    def __thresh_sat(self,img=[],thresh=(0,255)):
        hls = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
        s_channel = hls[:,:,2]
        s_binary = np.zeros_like(s_channel)
        s_binary[(s_channel >= thresh[0]) & (s_channel <= thresh[1])] = 1

        return s_binary

    def __thresh_gradx(self,img=[],sobel_kernel=3,thresh=(0, 255)):
        sobel = cv2.Sobel(img, cv2.CV_64F, 1, 0,ksize=sobel_kernel)
        abs_sobel = np.absolute(sobel)
        scaled_sobel = np.uint8(255*abs_sobel/np.max(abs_sobel))
        grad_binary = np.zeros_like(scaled_sobel)
        grad_binary[(scaled_sobel >= thresh[0]) & (scaled_sobel <= thresh[1])] = 1

        return grad_binary

    def __thresh_grady(self,img=[],sobel_kernel=3,thresh=(0,255)):
        sobel = cv2.Sobel(img, cv2.CV_64F, 0, 1,ksize=sobel_kernel)
        abs_sobel = np.absolute(sobel)
        scaled_sobel = np.uint8(255*abs_sobel/np.max(abs_sobel))
        grad_binary = np.zeros_like(scaled_sobel)
        grad_binary[(scaled_sobel >= thresh[0]) & (scaled_sobel <= thresh[1])] = 1

        return grad_binary

    def __thresh_mag(self,img=[],sobel_kernel=3,thresh=(0,255)):
        sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0,ksize=sobel_kernel)
        sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1,ksize=sobel_kernel)
        abs_sobelxy = np.sqrt(np.power(sobelx,2)+np.power(sobely,2))
        scaled_sobel = np.uint8(255*abs_sobelxy/np.max(abs_sobelxy))
        mag_binary = np.zeros_like(scaled_sobel)
        mag_binary[(scaled_sobel >= thresh[0]) & (scaled_sobel <= thresh[1])] = 1

        return mag_binary

    def __thresh_dir(self,img=[],sobel_kernel=3,thresh=(0,np.pi/2)):
        sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0,ksize=sobel_kernel)
        sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1,ksize=sobel_kernel)
        abs_sobelx = np.absolute(sobelx)
        abs_sobely = np.absolute(sobely)
        dir_grad=np.arctan2(abs_sobely,abs_sobelx)
        dir_binary = np.zeros_like(dir_grad)
        dir_binary[(dir_grad > thresh[0]) & (dir_grad < thresh[1])] = 1

        return dir_binary

    def combinator_gradients(self,img=[],params={}):
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        combined = np.zeros_like(img)
        if params["gradx"]["act"] == 1:
            gradx=self.__thresh_gradx(img,params["gradx"]["kernel"],params["gradx"]["thresh"])
        else:
            gradx=np.ones_like(img)
        if params["grady"]["act"]==1:
            grady=self.__thresh_grady(img,params["grady"]["kernel"],params["grady"]["thresh"])
        else:
            grady=np.ones_like(img)
        if params["mag"]["act"]==1:
            mag_binary=self.__thresh_mag(img,params["mag"]["kernel"],params["mag"]["thresh"])
        else:
            mag_binary=np.ones_like(img)
        if params["dir"]["act"]==1:
            dir_binary=self.__thresh_dir(img,params["dir"]["kernel"],params["dir"]["thresh"])
        else:
            dir_binary=np.ones_like(img)
        if params["gradx"]["act"] ==0 and params["grady"]["act"]==0:
            combined[((mag_binary == 1) & (dir_binary == 1))] = 1
        elif params["mag"]["act"] == 0 and params["dir"]["act"]== 0:
            combined[((gradx == 1) & (grady == 1))] = 1
        else:
            combined[((gradx == 1) & (grady == 1)) | ((mag_binary == 1) & (dir_binary == 1))] = 1
        if params["gradx"]["act"]==0 and params["grady"]["act"]==0 and params["mag"]["act"]==0 and params["dir"]["act"]==0:

            return img
        return combined*255
    def combinator_colors(self,img=[],params={}):
        combined = np.zeros_like(img[:,:,1])
        if params["lum"]["act"] ==1:
            lum=self.__thresh_lum(img,params["lum"]["thresh"])
        else:
            lum=np.ones_like(img[:,:,1])
        if params["sat"]["act"]==1:
            sat=self.__thresh_sat(img,params["sat"]["thresh"])
        else:
            sat=np.ones_like(img[:,:,1])

        if params["lum"]["act"]==0 and params["sat"]["act"]==0:
            return img
        else:
            combined[((sat == 1) & (lum == 1))] = 1
            return combined*255

    def gradient_and_color(self,img1,img2):
        aux=np.zeros_like(img1)
        if len(np.shape(img1))== 3:
            aux=np.zeros_like(img1[:,:,1])
            img1=np.zeros_like(img1[:,:,1])
        if len(np.shape(img2))==3:
            aux=np.zeros_like(img2[:,:,1])
            img2=np.zeros_like(img2[:,:,1])

        color_binary = np.dstack((aux, img1, img2))
        return color_binary

    def resize_image(self,img=[],scale_percent=60):
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        return resized

    def image2gui(self,img=[]):
        img=cv2.imencode(".png",img)[1].tobytes()
        return img

    def select_points(self,img=[]):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        plt.imshow(img)
        points = plt.ginput(4)
        points= np.array(list(list(tup) for tup in points))
        plt.show()
        return np.array(points)

    def perspective(self,img,ori_pts):
        dst_pts = np.float32([[0,int(img.shape[0])],[0,0],[int(img.shape[1]),0],[int(img.shape[1]),int(img.shape[0])]])
        self.Minv = cv2.getPerspectiveTransform(dst_pts,np.float32(ori_pts))
        self.M = cv2.getPerspectiveTransform(np.float32(ori_pts), np.float32(dst_pts))
        warped = cv2.warpPerspective(img, self.M, (img.shape[1],img.shape[0]), flags=cv2.INTER_LINEAR)
        return warped
