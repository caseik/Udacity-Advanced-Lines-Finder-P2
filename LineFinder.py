import numpy as np
import cv2
import time
class Line():
    def __init__(self,n=4,average=True):
        self.lists_of_fits = []
        self.current_fit = [np.array([False])]
        #radius of curvature of the line in some units
        self.radius_of_curvature = None
        self.idx = 0
    def avg_fits(self):
        if len(self.lists_of_fits) < 5:
            self.lists_of_fits.append(self.current_fit)
            return self.current_fit
        else:
            self.lists_of_fits[self.idx]=(self.current_fit)
            self.idx = self.idx +1
            if self.idx == 5:
                self.idx=0
            return np.mean(self.lists_of_fits, axis=0)
        

class LineFinder():
    def __init__(self):
        self.list_of_widnows= []
        self.sanity =False
        self.center_offset=0
        self.radius_of_curvature =0
    def __center_calculation(self,img,left_fitx,right_fitx):
        xm_per_pix = 3.7/700 
        lane_center = (left_fitx[-1] + right_fitx[-1])//2
        car_center = img.shape[1]/2  
        self.center_offset = (lane_center - car_center) * xm_per_pix

    def __radius_calculation(self,img,leftx,rightx,lefty,righty):

        ym_per_pix = 30/720 
        xm_per_pix = 3.7/700 

        left_fit_cr = np.polyfit(lefty*ym_per_pix, leftx*xm_per_pix,2)
        right_fit_cr = np.polyfit(righty*ym_per_pix, rightx*xm_per_pix,2)
        ploty = np.linspace(0, img.shape[0]-1, img.shape[0] )

        y_eval = np.max(ploty*ym_per_pix)
      
        f1l = (2*left_fit_cr[0]*y_eval+left_fit_cr[1])
        f1r = (2*right_fit_cr[0]*y_eval+right_fit_cr[1])
        numerador_l =(1+f1l**2)**1.5
        numerador_r =(1+f1r**2)**1.5
        f2l = 2*left_fit_cr[0]
        f2r = 2*right_fit_cr[0]
        left_curverad = numerador_l/np.absolute(f2l)  
        right_curverad = numerador_r/np.absolute(f2r) 
    
        return left_curverad, right_curverad

    def __look_ahead(self,img,hiperparameters):
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        out_img = np.dstack((img, img, img))
        margin=50
        nwindows=hiperparameters["nwindows"]
        minpix=hiperparameters["minpix"]
        window_height = np.int(img.shape[0]//nwindows)
        nonzero = img.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])

        
        left_lane_inds = []
        right_lane_inds = []
        
        for window in range(nwindows):
            win_y_low = img.shape[0] - (window+1)*window_height
            win_y_high = img.shape[0] - window*window_height
            win_xleft_low = self.list_of_widnows[window][0]-margin
            win_xleft_high = self.list_of_widnows[window][1] + margin
            win_xright_low = self.list_of_widnows[window][2] -margin
            win_xright_high = self.list_of_widnows[window][3] + margin
           
            # Draw the windows on the visualization image
            cv2.rectangle(out_img,(win_xleft_low,win_y_low),(win_xleft_high,win_y_high),(0,255,0), 2)
            cv2.rectangle(out_img,(win_xright_low,win_y_low),(win_xright_high,win_y_high),(0,255,0), 2)

            left_low = nonzerox >= win_xleft_low
            left_high = nonzerox < win_xleft_high
            y_low = nonzeroy >= win_y_low
            y_high = nonzeroy < win_y_high
            right_low = nonzerox >= win_xright_low
            right_high = nonzerox < win_xright_high



            left_bool= np.logical_and(y_high,np.logical_and(y_low, np.logical_and(left_low,left_high)))
            right_bool= np.logical_and(y_high,np.logical_and(y_low, np.logical_and(right_low,right_high)))

            good_left_inds = np.where(left_bool == True)[0]
            good_right_inds =np.where(right_bool == True)[0]

            # Append these indices to the lists
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)
            if minpix > len(good_left_inds):
                self.sanity =False

            if minpix > len(good_right_inds):
                self.sanity =False
        try:
            left_lane_inds = np.concatenate(left_lane_inds)
            right_lane_inds = np.concatenate(right_lane_inds)
        except ValueError:
            pass
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds]
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]
        
        return leftx, lefty, rightx, righty, out_img

    def __find_lane_pixels(self,img,hiperparameters):
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        histogram = np.sum(img[img.shape[0]//2:,:], axis=0)
        out_img = np.dstack((img, img, img))
        midpoint = np.int(histogram.shape[0]//2)
        leftx_base = np.argmax(histogram[:midpoint])
        rightx_base = np.argmax(histogram[midpoint:]) + midpoint
        nwindows=hiperparameters["nwindows"]
        margin=hiperparameters["margin"]
        minpix=hiperparameters["minpix"]
        window_height = np.int(img.shape[0]//nwindows)
        nonzero = img.nonzero()
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])

        leftx_current = leftx_base
        rightx_current = rightx_base
        left_lane_inds = []
        right_lane_inds = []

        list_of_widnows=[]
        for window in range(nwindows):
            win_y_low = img.shape[0] - (window+1)*window_height
            win_y_high = img.shape[0] - window*window_height
            win_xleft_low = leftx_current -margin
            win_xleft_high = leftx_current + margin
            win_xright_low = rightx_current -margin
            win_xright_high = rightx_current + margin
            marging_of_windows=[win_xleft_low, win_xleft_high,win_xright_low,win_xright_high]
            list_of_widnows.append(marging_of_windows)
            # Draw the windows on the visualization image
            cv2.rectangle(out_img,(win_xleft_low,win_y_low),(win_xleft_high,win_y_high),(0,255,0), 2)
            cv2.rectangle(out_img,(win_xright_low,win_y_low),(win_xright_high,win_y_high),(0,255,0), 2)

            left_low = nonzerox >= win_xleft_low
            left_high = nonzerox < win_xleft_high
            y_low = nonzeroy >= win_y_low
            y_high = nonzeroy < win_y_high
            right_low = nonzerox >= win_xright_low
            right_high = nonzerox < win_xright_high



            left_bool= np.logical_and(y_high,np.logical_and(y_low, np.logical_and(left_low,left_high)))
            right_bool= np.logical_and(y_high,np.logical_and(y_low, np.logical_and(right_low,right_high)))

            good_left_inds = np.where(left_bool == True)[0]
            good_right_inds =np.where(right_bool == True)[0]

            # Append these indices to the lists
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)


            if minpix < len(good_left_inds):
                leftx_current=np.int(np.mean(nonzerox[good_left_inds]))

            if minpix < len(good_right_inds):
                rightx_current= np.int(np.mean(nonzerox[good_right_inds]))
        try:
            left_lane_inds = np.concatenate(left_lane_inds)
            right_lane_inds = np.concatenate(right_lane_inds)
        except ValueError:
            pass
        leftx = nonzerox[left_lane_inds]
        lefty = nonzeroy[left_lane_inds]
        rightx = nonzerox[right_lane_inds]
        righty = nonzeroy[right_lane_inds]
        self.list_of_widnows=list_of_widnows
        
       
        return leftx, lefty, rightx, righty, out_img
    def __sanity_check(self,LineL,LineR):
        if np.abs(LineL.radius_of_curvature-LineR.radius_of_curvature)>1000:
             self.sanity =False
        
        
        if  self.radius_of_curvature >10000:
            self.sanity =False
        else:
            self.sanity =True
    def fit_polynomial(self,img,hiperparameters,LineL,LineR):
        if self.sanity==False:
            leftx, lefty, rightx, righty, out_img =self.__find_lane_pixels(img,hiperparameters)
        else:
            leftx, lefty, rightx, righty, out_img =self.__look_ahead(img,hiperparameters)
        try:
            left_fit = np.polyfit(lefty, leftx,2)
            right_fit = np.polyfit(righty,rightx,2)
        except Exception:
            print("Can not find the Lane!!!")
            self.sanity =False
            return img
        LineR.current_fit=right_fit
        LineL.current_fit=left_fit


        ploty = np.linspace(0, img.shape[0]-1, img.shape[0] )
        try:
            left_fitx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
            right_fitx = right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]
            [LineL.radius_of_curvature, LineR.radius_of_curvature]=self.__radius_calculation(img,leftx,rightx,lefty,righty)
        except TypeError:
            print('The function failed to fit a line!')
            left_fitx = 1*ploty**2 + 1*ploty
            right_fitx = 1*ploty**2 + 1*ploty

        
        out_img[lefty, leftx] = [255, 0, 0]
        out_img[righty, rightx] = [0, 0, 255]

        left_line=list(zip(left_fitx, ploty))
        left_line=np.array(left_line,np.int32)
        right_line=list(zip(right_fitx,ploty))
        right_line=np.array(right_line,np.int32)
        color=(0,255,255)
        thickness=2
        out_img = cv2.polylines(out_img,[left_line],False,color,thickness)
        out_img = cv2.polylines(out_img,[right_line],False,color,thickness)
        self.__center_calculation(img,left_fitx,right_fitx)
        return out_img


    def draw_lines(self,img,img_ori,LineL,LineR,Minv):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ploty = np.linspace(0, img.shape[0]-1, img.shape[0] )
        try:
            avg_L_fit=LineL.avg_fits()
            avg_R_fit=LineR.avg_fits()
            left_fitx = avg_L_fit[0]*ploty**2 + avg_L_fit[1]*ploty + avg_L_fit[2]
            right_fitx = avg_R_fit[0]*ploty**2 + avg_R_fit[1]*ploty + avg_R_fit[2]
        except TypeError:
            print('The function failed to fit a line!')
            
            left_fitx = 1*ploty**2 + 1*ploty
            right_fitx = 1*ploty**2 + 1*ploty
        LineR.recent_xfitted = right_fitx
        LineL.recent_xfitted = left_fitx
        warp_zero = np.zeros_like(gray).astype(np.uint8)
        color_warp = np.dstack((warp_zero, warp_zero, warp_zero))

        # Recast the x and y points into usable format for cv2.fillPoly()
        pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
        pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
        pts = np.hstack((pts_left, pts_right))

        cv2.fillPoly(color_warp, np.int_([pts]), (0,255, 0))

        newwarp = cv2.warpPerspective(color_warp, Minv, (gray.shape[1], gray.shape[0]))
        result = cv2.addWeighted(img_ori, 1, newwarp, 0.3, 0)

        self.radius_of_curvature = (LineL.radius_of_curvature  + LineR.radius_of_curvature)/2
        self.__sanity_check(LineL,LineR)
        cv2.putText(result, "Radius of the curvature : " + str('%.2f' % self.radius_of_curvature),(50,50),cv2.FONT_HERSHEY_SIMPLEX,1,[255,255,255],2, cv2.LINE_AA)
        cv2.putText(result, "Vehicle is: " + str('%.2f' % self.center_offset) + "m of the center",(50,100),cv2.FONT_HERSHEY_SIMPLEX,1,[255,255,255],2, cv2.LINE_AA)

        return result
