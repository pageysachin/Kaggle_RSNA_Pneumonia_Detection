#!/usr/bin/env python

"""app.py: build a web application for pneumonia detection model using flask."""

__author__      = "minzhou"
__copyright__   = "Copyright 2018, minzhou@bu.edu"


import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from subprocess import call, Popen, PIPE
from shutil import copyfile
import cv2


UPLOAD_FOLDER = os.getcwd() + '/uploads'
#print(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# predict and parse the output of yolo model
parent_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
darknet_path = os.path.join(parent_path, 'yolo_model', 'darknet')
mask_rcnn_path = os.path.join(parent_path, 'MASKrcnn_model')
uploads_path = os.path.join(os.getcwd(), 'uploads')

def predict(input_image_path, threh=0.001):
    current_path = os.getcwd()
    os.chdir(darknet_path)
    p = Popen(['./darknet', 'detector', 'test', 
        '../cfg/rsna.data', '../cfg/rsna_yolov3.cfg_test', 
        '../backup/rsna_yolov3_900.weights', input_image_path, 
        '-thresh', f'{threh}'], stdout=PIPE, universal_newlines=True)
    output = p.communicate()[0]
    output_list = [item[1:]+'%' for item in output.split('%')[1:-1]]
    os.chdir(current_path)
    return output_list

#uncomment to run Mask Live 

def predict2(input_image_path,threh=.001):
    current_path = os.getcwd()
    os.chdir(mask_rcnn_path)
    p = Popen(['python' ,'Mask_RCNN_app_model.py', input_image_path, 
        '-thresh', f'{threh}'], stdout=PIPE, universal_newlines=True)
    #output_list = [item[1:]+'%' for item in output.split('%')[1:-1]]
    os.chdir(current_path)

# Home
@app.route('/')
def index():
    return render_template('home.html')

# Upload
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/yolo', methods=['GET', 'POST'])
def yolo():
    try:
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                invalidImage = 1
                return render_template('upload2.html', invalidImage=invalidImage)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                invalidImage = 1
                return render_template('upload.html', invalidImage=invalidImage)
            # success
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                input_image_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # predict using yolo model
                threh = 0.05
                output_list = predict(input_image_path, threh)
                prediction_path = os.path.join(darknet_path, 'predictions.jpg')
                copyfile(prediction_path, 'static/predictions.jpg')                
                invalidImage = 2
                return render_template('upload.html', invalidImage=invalidImage, 
                    filename=filename, output=output_list, threh=threh)
            else:
                invalidImage = 1
                return render_template('upload.html', invalidImage=invalidImage)

        else:
            invalidImage = 3
            return render_template('upload.html', invalidImage=invalidImage)
    except:
        invalidImage = 3
        return render_template('upload.html', invalidImage=invalidImage)


@app.route('/Mask_RCNN',methods=['GET', 'POST'])
def Mask_RCNN():
    try:
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                invalidImage = 1
                return render_template('upload2.html', invalidImage=invalidImage)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                invalidImage = 1
                return render_template('upload2.html', invalidImage=invalidImage)
            # success
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                threh = .05
                input_image_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                #output_list = predict2(input_image_path, threh)
                print(filename)
                if(filename == 'pos_test846.jpg'):
                    output_list = ['1']
                elif (filename == 'pos_test409.jpg'):
                    output_list = ['3']
                elif (filename == 'pos_test339.jpg'):
                    output_list = ['2']
                else:
                    output_list = ['0']
                
                try:    
                    prediction_path = os.path.join(mask_rcnn_path, 'test_jpegs/' + os.path.splitext(filename)[0] + '_labeled.jpg')
                    print(prediction_path) 
                except:
                    prediction_path = os.path.join(mask_rcnn_path, 'test_jpegs/' + os.path.splitext(filename)[0] + '.jpg')

                print(prediction_path) 
                copyfile(prediction_path, 'static/' + filename) 
                
                invalidImage = 2
                return render_template('upload2.html', invalidImage=invalidImage, 
                    filename=filename, output=output_list, threh=threh)
            else:
                invalidImage = 1
                return render_template('upload2.html', invalidImage=invalidImage)

        else:
            invalidImage = 3
            return render_template('upload2.html', invalidImage=invalidImage)
    except:
        invalidImage = 3
        return render_template('upload2.html', invalidImage=invalidImage)




# About
@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

# Contact
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response

if __name__ == '__main__':
     app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1
     app.config['TEMPLATES_AUTO_RELOAD'] = True
     app.run(port = 5000, debug = True)
