from camera import Camera
from image_editor import ImageEditor
import pickle
import PySimpleGUI as sg
from LineFinder import LineFinder,Line
import numpy as np
import os


lineF = LineFinder()
cam1=Camera()
editor=ImageEditor()

points={}
LineL=Line()
LineR=Line()
params ={ 'gradx': {"kernel": 3, "thresh":(20,120), "act": 0},
            'grady': {"kernel": 3, "thresh":(20,120), "act": 0},
            'mag':   {"kernel": 3, "thresh":(20,120), "act": 0},
            'dir':   {"kernel": 3, "thresh":(20,120), "act": 0},
            'lum':   {"thresh":(20,120), "act": 0},
            'sat':   {"thresh":(20,120), "act": 0}
            }
mode_idx=0
Mode = ["Mode","Gradient", "Color","Both"]
layout=[
        [
        sg.FolderBrowse(button_text="Select data folder ",key="-SELECT-"),
        sg.Button(key="-LOAD-",button_text="Load data",button_color="blue"),
        sg.Button(key="-SAVE-",button_text="Save data"),
        sg.Button(key="-SAVEIMAGES-",button_text="Save video/images"),
        sg.Button(key="-SAVEDEBUG-",button_text="Save Debug Images"),

        ],
        [
         sg.Button(key="-LOADPICS-",button_text="Load pictures"),
         sg.Button(key="-LOADVIDS-",button_text="Load video"),
         sg.Button(key="-CALCAM-",button_text="Calibrate Camera",button_color="gray"),
         sg.Button(key="-STOP-",button_text="STOP",button_color="gray"),
         sg.Button(key="-SHOW-",button_text="Show result",button_color="gray"),
        
        ],
        [   sg.Text("GradientX"),
            sg.Button("OFF",size=(10,1),key="-GRADX-",button_color="gray"),
            sg.Slider((0,255),128,1,orientation="h",size=(20,15),key="-GRADXA-"),
            sg.Slider((0,255),128,1,orientation="h",size=(20,15),key="-GRADXB-"),
            sg.Text("kernel",key= "KERXT"),
            sg.Slider((1, 11),1,2,orientation="h",size=(20,15),key="-KERX-"),
            sg.Text("Luminosity"),
            sg.Button("OFF",size=(10,1),key="-LUM-",button_color="gray"),
            sg.Slider((0,255),128,1,orientation="h",size=(20,15),key="-LUMA-"),
            sg.Slider((0,255),128,1,orientation="h",size=(20,15),key="-LUMB-")
        ],
        [
            sg.Text("GradientY"),
            sg.Button("OFF",size=(10,1),key="-GRADY-",button_color="gray"),
            sg.Slider((0,255),128,1,orientation="h",size=(20,15),key="-GRADYA-"),
            sg.Slider((0,255),128,1,orientation="h",size=(20,15),key="-GRADYB-"),
            sg.Text("kernel",key= "KERYT"),
            sg.Slider((1, 11),1,2,orientation="h",size=(20,15),key="-KERY-"),
        ],
        [
            sg.Text("Gradient Mag"),
            sg.Button("OFF",size=(10,1),key="-GRADM-",button_color="gray"),
            sg.Slider((0,255),128,1,orientation="h",size=(20,15),key="-GRADMA-"),
            sg.Slider((0,255),128,1,orientation="h",size=(20,15),key="-GRADMB-"),
            sg.Text("kernel",key= "KERMT"),
            sg.Slider((1, 11),1,2,orientation="h",size=(20,15),key="-KERM-"),
        ],
        [
            sg.Text("Gradient Dir"),
            sg.Button("OFF",size=(10,1),key="-GRADD-",button_color="gray"),
            sg.Slider((-np.pi/2,np.pi/2),0,np.pi/32,orientation="h",size=(20,15),key="-GRADDA-"),
            sg.Slider((-np.pi/2,np.pi/2),0,np.pi/32,orientation="h",size=(20,15),key="-GRADDB-"),
            sg.Text("kernel",key= "KERDT"),
            sg.Slider((1, 11),1,2,orientation="h",size=(20,15),key="-KERD-"),
            sg.Text("Saturation"),
            sg.Button("OFF",size=(10,1),key="-SAT-",button_color="gray"),
            sg.Slider((0,255),128,1,orientation="h",size=(20,15),key="-SATA-"),
            sg.Slider((0,255),128,1,orientation="h",size=(20,15),key="-SATB-")
        ],
        [
         sg.Button(key="-NEXT-",button_text="NEXT"),
         sg.Button(key="-TRANSFORM-",button_text="Persepctive Transform"),
         sg.Button(key="-EDITMODE-",button_text=Mode[mode_idx]),
        ],
        [
         sg.Image(key="-ORI-"),
         sg.Image(key="-MODE-"),
        ],
        [
         sg.Image(key="-OUT-"),
         sg.Image(key="-AUX-"),
        ],
        ]
window=sg.Window("Advanced line finder",layout)
cam1.calibrate_camera(9,6,"camera_cal/")
hiperparameters ={"nwindows": 10, "margin": 100, "minpix":50}
index=0
cursor =0
img =  np.zeros(shape=(720, 1280, 3), dtype=np.uint8)
displayed_images= [img]
videos=0
stoped=False
calibration = False
transformed = False
find_lines = False
loaded = False
while True:
    event,values=window.read(timeout=20)
    if event == sg.WINDOW_CLOSED:
        break
    if event == "-LOADPICS-":
        displayed_images = cam1.load_images_in_folder("test_images/")
        videos=0
        index=0
    if event == "-LOADVIDS-":
        displayed_images = cam1.load_videos_in_folder("test_videos/")
        videos=1
        index=0

    if event == "-LOAD-":
        if loaded == False:
            if  values["-SELECT-"]:
                fileparams= open(os.path.join(values["-SELECT-"], "params.pkl"),"rb")
                loadparams = pickle.load(fileparams)
                fileparams.close()

                filepoints= open(os.path.join(values["-SELECT-"], "points.pkl"),"rb")
                loadpoints = pickle.load(filepoints)
                filepoints.close()
                loaded = True
                window[event].update(text="LOADED")
                window[event].update(button_color="red")
            else:
                print("Select a folder")
        else:
            loaded = False
            window[event].update(text="LOADED")
            window[event].update(button_color="blue")

 
 
        
    if event == "-SAVE-":
        if points: 
            if  values["-SELECT-"]:
                file = open(os.path.join(values["-SELECT-"], "params.pkl"),"wb")
                pickle.dump(params, file)
                file.close()

                file = open(os.path.join(values["-SELECT-"], "points.pkl"),"wb")
                pickle.dump(points,file)
                file.close()
            else:
                print("Select a folder")

        else:
            print("No points to save")
   
    if event == "-GRADX-":
            if window[event].get_text() == "OFF":
                window[event].update(text="ON")
                window[event].update(button_color="green")
                params["gradx"]["act"]=1
            elif window[event].get_text() == "ON":
                window[event].update(text="OFF")
                params["gradx"]["act"]=0
                window[event].update(button_color="gray")
    if params["gradx"]["act"] == 1:
        params["gradx"]["kernel"]=int(values["-KERX-"])
        params["gradx"]["thresh"]=(int(values["-GRADXA-"]),int(values["-GRADXB-"]))

    if event == "-GRADY-":
        if window[event].get_text() == "OFF":
            window[event].update(text="ON")
            window[event].update(button_color="green")
            params["grady"]["act"]=1
        elif window[event].get_text() == "ON":
            window[event].update(text="OFF")
            params["grady"]["act"]=0
            window[event].update(button_color="gray")

    if params["grady"]["act"] == 1:
        params["grady"]["kernel"]=int(values["-KERY-"])
        params["grady"]["thresh"]=(int(values["-GRADYA-"]),int(values["-GRADYB-"]))

    if event == "-GRADM-":
        if window[event].get_text() == "OFF":
            window[event].update(text="ON")
            window[event].update(button_color="green")
            params["mag"]["act"]=1
        elif window[event].get_text() == "ON":
            window[event].update(text="OFF")
            params["mag"]["act"]=0
            window[event].update(button_color="gray")
    if params["mag"]["act"] == 1:
        params["mag"]["kernel"]=int(values["-KERM-"])
        params["mag"]["thresh"]=(int(values["-GRADMA-"]),int(values["-GRADMB-"]))

    if event == "-GRADD-":
        if window[event].get_text() == "OFF":
            window[event].update(text="ON")
            window[event].update(button_color="green")
            params["dir"]["act"]=1
        elif window[event].get_text() == "ON":
            window[event].update(text="OFF")
            params["dir"]["act"]=0
            window[event].update(button_color="gray")
    if params["dir"]["act"] == 1:
        params["dir"]["kernel"]=int(values["-KERD-"])
        params["dir"]["thresh"]=(values["-GRADDA-"],values["-GRADDB-"])

    if event == "-LUM-":
        if window[event].get_text() == "OFF":
            window[event].update(text="ON")
            window[event].update(button_color="green")
            params["lum"]["act"]=1
        elif window[event].get_text() == "ON":
            window[event].update(text="OFF")
            params["lum"]["act"]=0
            window[event].update(button_color="gray")
    if params["lum"]["act"] == 1:
        params["lum"]["thresh"]=(values["-LUMA-"],values["-LUMB-"])

    if event == "-SAT-":
        if window[event].get_text() == "OFF":
            window[event].update(text="ON")
            window[event].update(button_color="green")
            params["sat"]["act"]=1
        elif window[event].get_text() == "ON":
            window[event].update(text="OFF")
            params["sat"]["act"]=0
            window[event].update(button_color="gray")
    if params["sat"]["act"] == 1:
        params["sat"]["thresh"]=(values["-SATA-"],values["-SATB-"])
   
    if event == "-NEXT-":
        index=index+1
        cursor=0
        if len(displayed_images)==index:
            index=0
        displayed_images[index] 
    
    if videos==0:
        img = displayed_images[index]
        
    else:
        if stoped == True:
            cursor=cursor
            if len(displayed_images[index])==cursor:
                cursor=0
            img = displayed_images[index][cursor]
        else:
            cursor=cursor +1
            if len(displayed_images[index])==cursor:
                cursor=0
            img = displayed_images[index][cursor]

    if event == "-STOP-":
        if stoped == False:
            stoped = True
            window[event].update(text="PLAY")
            window[event].update(button_color="green")
        else:
            stoped = False
            window[event].update(text="STOP")
            window[event].update(button_color="gray")

    if event == "-EDITMODE-":
        mode_idx=mode_idx+1
        if len(Mode)==mode_idx:
            mode_idx=0
        window[event].update(text=Mode[mode_idx])
  
    if event == "-CALCAM-":
        if calibration == False:
            calibration = True
            window[event].update(button_color="green")
        elif calibration == True:
            calibration = False
            window[event].update(button_color="gray")
    if calibration == True:
        img=cam1.undistort_image(img)
    
    if event == "-TRANSFORM-":
        ori_pts=editor.select_points(img)
        points = {"ori": ori_pts}
        transformed = True
  

    if loaded == False:
        img_tr = img.copy()
        img_grad=editor.combinator_gradients(img,params)
        img_color =editor.combinator_colors(img,params)
        img_res =editor.gradient_and_color(img_grad,img_color)

        if transformed==True:
            img_tr=editor.perspective(img_res,ori_pts)
    else:
        img_tr = img.copy()
        img_grad=editor.combinator_gradients(img,loadparams)
        img_color =editor.combinator_colors(img,loadparams)
        img_res =editor.gradient_and_color(img_grad,img_color)

        img_tr=editor.perspective(img_res,loadpoints["ori"])
     
    if Mode[mode_idx] == "Gradient":
        window["-MODE-"].update(data=editor.image2gui(editor.resize_image(img_grad,50)))
    elif Mode[mode_idx] == "Color":
        window["-MODE-"].update(data=editor.image2gui(editor.resize_image(img_color,50)))
    elif Mode[mode_idx] == "Both":
        window["-MODE-"].update(data=editor.image2gui(editor.resize_image(img_res,50)))    
    else:
        window["-MODE-"].update(data=editor.image2gui(editor.resize_image(img,50)))

    
    window["-ORI-"].update(data=editor.image2gui(editor.resize_image(img,50)))
    if event == "-SHOW-":
        if find_lines == False:
            find_lines = True
            window[event].update(text="OFF")
            window[event].update(button_color="red")
        else: 
            find_lines = False
            window[event].update(text="Show result")
            window[event].update(button_color="gray")
      
    if find_lines == True:
        img_lin=lineF.fit_polynomial(img_tr,hiperparameters,LineL,LineR)
        img_tr=img_lin
        img_draw=lineF.draw_lines(img_lin,img,LineL,LineR,editor.Minv)
    else:

        img_draw = img.copy()
    window["-OUT-"].update(data=editor.image2gui(editor.resize_image(img_draw,50))) 
    
    window["-AUX-"].update(data=editor.image2gui(editor.resize_image(img_tr,50)))
    if event =="-SAVEDEBUG-":
        cam1.DEBUG_draw_corners(horizontal_corners=9,vertical_corners=6,output_path='output/draw_corners/',input_path='camera_cal/')
        cam1.DEBUG_draw_undistort_images(input_path='camera_cal',output_path='output/cal_images')
    if event == "-SAVEIMAGES-":
        result=[]
        debug=[]
        if videos ==1 and loaded == True:
            for img in displayed_images[index]:
                img=cam1.undistort_image(img)
                img_grad=editor.combinator_gradients(img,loadparams)
                img_color =editor.combinator_colors(img,loadparams)
                img_res =editor.gradient_and_color(img_grad,img_color)
                img_tr=editor.perspective(img_res,loadpoints["ori"])
                img_lin=lineF.fit_polynomial(img_tr,hiperparameters,LineL,LineR)
                img_draw=lineF.draw_lines(img_lin,img,LineL,LineR,editor.Minv)
                debug.append(img_lin)
                result.append(img_draw)
                
            cam1.save_video(result,output_path='output/video/',video_name='video_result.avi',FPS=25)
            cam1.save_video(debug,output_path='output/video/',video_name='debug.avi',FPS=25)
        elif videos ==0 and loaded == True:
            img_grad=editor.combinator_gradients(img,loadparams)
            img_color =editor.combinator_colors(img,loadparams)
            img_res =editor.gradient_and_color(img_grad,img_color)
            img_tr=editor.perspective(img_res,loadpoints["ori"])
            img_lin=lineF.fit_polynomial(img_tr,hiperparameters,LineL,LineR)

            cam1.save_image(img_draw,output_path="output/images",image_name="result.jpg")
            cam1.save_image(img_lin,output_path="output/images",image_name="debug.jpg")
        else:
            pass
window.close()

    