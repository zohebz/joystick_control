#! /usr/bin/python
import serial           # import using pip
import time
import cv2
import numpy as np
import ast
import random
import csv
import pygame

#blue - start point
#red -  end point
#green - joystick

arduino = serial.Serial('COM7', 9600, timeout=0.1)

def check_reset(data):
    if 'reset' in data:
        return True
    return False

def show_plot(coordinates,random_points,calibrated_max_min,reset):
    moving_point_color = (0,255,0)
    end_point_color = (255,0,0)
    start_point_color = (0,0,255)
    x_range = calibrated_max_min["x_max"] - calibrated_max_min["x_min"]
    y_range = calibrated_max_min["y_max"] - calibrated_max_min["y_min"]
    view = np.zeros((x_range, y_range, 3), dtype = "uint8")
    if not reset:
        view = cv2.circle(view, (coordinates[0]-calibrated_max_min["x_min"],coordinates[1]-calibrated_max_min["x_min"]), radius=5, color=moving_point_color, thickness=-1)
        view = cv2.circle(view, (random_points[len(random_points)-2][0]-calibrated_max_min["x_min"],random_points[len(random_points)-2][1]-calibrated_max_min["x_min"]), radius=5, color=start_point_color, thickness=-1)
        view = cv2.circle(view, (random_points[len(random_points)-1][0]-calibrated_max_min["x_min"],random_points[len(random_points)-1][1]-calibrated_max_min["x_min"]), radius=5, color=end_point_color, thickness=-1)
        return view
    else:
        return view

def check_final_reach(coordinates,random_points):
    x_reached = False
    y_reached = False
    if abs(coordinates[0] - random_points[len(random_points)-1][0]) < 5:
        x_reached = True
    if abs(coordinates[1] - random_points[len(random_points)-1][1]) < 5:
        y_reached = True
    if x_reached and y_reached:
        return True
    return False

def get_coordinates(data):
    coordinates = [None,None]
    if "X:" in data and "| Y:" in data:
        coordinates[0]= int(data.split("X:")[1].split("| Y:")[0])
        coordinates[1]= int(data.split("X:")[1].split("| Y:")[1])
    return coordinates
           

def write_read(x):
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = arduino.readline()
    return data

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
    write_read(mode)
    random_points = []
    random_points.append(generate_random_point(calibrated_max_min))
    random_points.append(generate_random_point(calibrated_max_min))

    f_csv = open('observation.csv', 'w',newline='')
    writer_csv = csv.writer(f_csv)
    writer_csv.writerow(csv_headers)

    print('print values')
    while True:
        rawdata = arduino.readline()
        data = str(rawdata.decode('utf-8'))
        current_time = time.time()
        #print(data)
        if check_reset(data):
            show_plot(coordinates,random_points,calibrated_max_min,True)
            mode =  input('enter mode: ')   
            write_read(mode)
        else:
            coordinates = get_coordinates(data)
            if coordinates[0]!=None and coordinates[1]!=None:
                view=show_plot(coordinates,random_points,calibrated_max_min,False)
                image = pygame.surfarray.make_surface(view)
                view_obj = pygame.display.set_mode((view.shape[0], view.shape[1]))
                view_obj.blit(image, (0, 0))
                pygame.display.update()
                if check_final_reach(coordinates,random_points):
                    random_points.append(generate_random_point(calibrated_max_min))
                    print('generate new points')
                write_data_to_file(coordinates,random_points,mode,current_time,writer_csv)
