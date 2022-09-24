#! /usr/bin/python
import csv
import ast
import time
import math
from PIL import Image
import numpy as np
import cv2
import os
import traceback
import random

def generate_random_point(calibrated_max_min):
    random_points = []
    random_points.append(random.randint(calibrated_max_min["x_min"]+10,calibrated_max_min["x_max"]-10))
    random_points.append(random.randint(calibrated_max_min["y_min"]+10,calibrated_max_min["y_max"]-10))
    return random_points

def write_data_to_file(coordinates,random_points,mode,time,writer):
    mode_str = None
    if mode == '1':
        mode_str = "Force Feedback OFF"
    if mode == '2':
        mode_str = "Force Feedback ON"
    end_pont=random_points[len(random_points)-1]
    start_point=random_points[len(random_points)-2]
    row = [time,coordinates,start_point,end_pont,mode_str]
    writer.writerow(row)

calibrated = True
keys_list = ["x_max","x_min","y_max","y_min"]
csv_headers = ["time","joystick_pos","start_point","end_point","mode"]
try:
    f=open("calibration_data.txt", "r")
    lines = f.readlines()
    calibrated_max_min = ast.literal_eval(lines[0])
    f.close()
except:
    calibrated = False
for key in  keys_list:
    if key not in calibrated_max_min:
        print('run calibration program!!!')
        calibrated = False

if calibrated:
    mode =  input('enter mode: ')
    random_points = []
    random_points.append(generate_random_point(calibrated_max_min))
    random_points.append(generate_random_point(calibrated_max_min))

    f_csv = open('observation.csv', 'w',newline='')
    writer_csv = csv.writer(f_csv)
    writer_csv.writerow(csv_headers)

    print('print values')
    for i in range(100):
        current_time = time.time()
        coordinates = generate_random_point(calibrated_max_min) 
        if coordinates[0]!=None and coordinates[1]!=None:
                write_data_to_file(coordinates,random_points,mode,current_time,writer_csv)

print('-----end-----')
