#! /usr/bin/python
import csv
import ast
import math
from PIL import Image
import numpy as np
import cv2
import os
import traceback

#create folder "results" in same directory

x_range_max_degrees = 30
y_range_max_degrees = 35
joystick_weight_kg = 0.2
force_radius_m = 0.09
moment_of_inertia = (1/3)*joystick_weight_kg*force_radius_m*force_radius_m

value_unit_dict = {'time': 'time (s)',
                    'joystick_pos' : 'joystick position',
                    'start_point' : 'start point',
                    'end_point' : 'end point',
                    'mode' : 'MODE',
                    'velocity': 'velocity (m/s)',
                    'velocity_X': 'velocity_X (m/s)',
                    'velocity_Y': 'velocity_Y (m/s)',
                    'acceleration': 'acceleration (m/(s^2))',
                    'acceleration_X': 'acceleration_X (m/(s^2))',
                    'acceleration_X': 'acceleration_X (m/(s^2))',
                    'force' : 'force (N)',
                    'force_X' : 'force_X (N)',
                    'force_Y' : 'force_Y (N)', 
                    }

try:
    f=open("calibration_data.txt", "r")
    lines = f.readlines()
    calibrated_max_min = ast.literal_eval(lines[0])
    f.close()
    x_range = calibrated_max_min["x_max"] - calibrated_max_min["x_min"]
    y_range = calibrated_max_min["y_max"] - calibrated_max_min["y_min"]
except:
    print('error in getting finding limits')

with open('observation.csv') as f:
    reader = csv.DictReader(f)
    calculate_row_list = []
    for row in reader:
        converted_dict = {'time': ast.literal_eval(row['time']), 'joystick_pos': ast.literal_eval(row['joystick_pos']), 'start_point': ast.literal_eval(row['start_point']), 'end_point': ast.literal_eval(row['end_point']), 'mode': row['mode']}
        calculate_row_list.append(converted_dict)
    print('csv length: '+str(len(calculate_row_list)))
    i=0
    while i<len(calculate_row_list):
        if 'velocity' not in calculate_row_list[i] and i!=len(calculate_row_list)-1:
            time_diff = calculate_row_list[i+1]['time']- calculate_row_list[i]['time']
            distance = math.hypot(((calculate_row_list[i+1]['joystick_pos'][0]-calculate_row_list[i]['joystick_pos'][0])*(x_range_max_degrees/(x_range)))*force_radius_m,((calculate_row_list[i+1]['joystick_pos'][1]-calculate_row_list[i]['joystick_pos'][1])*(x_range_max_degrees/(x_range)))*force_radius_m) 
            calculate_row_list[i]['velocity_X'] = (((calculate_row_list[i+1]['joystick_pos'][0]-calculate_row_list[i]['joystick_pos'][0])*(x_range_max_degrees/(x_range)))*force_radius_m)/time_diff 
            calculate_row_list[i]['velocity_Y'] = (((calculate_row_list[i+1]['joystick_pos'][1]-calculate_row_list[i]['joystick_pos'][1])*(x_range_max_degrees/(x_range)))*force_radius_m)/time_diff 
            calculate_row_list[i]['velocity'] = distance/time_diff
        elif 'velocity' not in calculate_row_list[i] and i==len(calculate_row_list)-1:
            calculate_row_list[i]['velocity_X'] = 0 
            calculate_row_list[i]['velocity_Y'] = 0
            calculate_row_list[i]['velocity'] = 0
        i=i+1
    i=0
    while i<len(calculate_row_list):
        if 'acceleration' not in calculate_row_list[i] and i!=len(calculate_row_list)-1:
            time_diff = calculate_row_list[i+1]['time']- calculate_row_list[i]['time']
            velocity_diff = math.hypot(calculate_row_list[i+1]['velocity_X']-calculate_row_list[i]['velocity_X'],calculate_row_list[i+1]['velocity_Y']-calculate_row_list[i]['velocity_Y'])
            calculate_row_list[i]['acceleration_X'] = (calculate_row_list[i+1]['velocity_X']-calculate_row_list[i]['velocity_X'])/time_diff
            calculate_row_list[i]['acceleration_Y'] = (calculate_row_list[i+1]['velocity_Y']-calculate_row_list[i]['velocity_Y'])/time_diff
            calculate_row_list[i]['acceleration'] = velocity_diff/time_diff
        elif 'acceleration' not in calculate_row_list[i] and i==len(calculate_row_list)-1:
            calculate_row_list[i]['acceleration_X'] = 0 
            calculate_row_list[i]['acceleration_Y'] = 0
            calculate_row_list[i]['acceleration'] = 0
        i=i+1
    i=0
    while i<len(calculate_row_list):
        if 'force' not in calculate_row_list[i] and i!=len(calculate_row_list)-1:
            time_diff = calculate_row_list[i+1]['time']- calculate_row_list[i]['time']
            calculate_row_list[i]['force_X'] = ((calculate_row_list[i]['acceleration_X']/force_radius_m)*moment_of_inertia)/force_radius_m 
            calculate_row_list[i]['force_Y'] = ((calculate_row_list[i]['acceleration_X']/force_radius_m)*moment_of_inertia)/force_radius_m 
            calculate_row_list[i]['force'] =  ((calculate_row_list[i]['acceleration']/force_radius_m)*moment_of_inertia)/force_radius_m 
        elif 'force' not in calculate_row_list[i] and i==len(calculate_row_list)-1:
            calculate_row_list[i]['force_X'] = 0 
            calculate_row_list[i]['force_Y'] = 0
            calculate_row_list[i]['force'] = 0
        i=i+1
    end_point_split_dict = {}
    i=0
    while i<len(calculate_row_list):
        if str(calculate_row_list[i]['end_point']) not in end_point_split_dict:
            end_point_split_dict[str(calculate_row_list[i]['end_point'])] = [calculate_row_list[i]]
        else:
            end_point_split_dict[str(calculate_row_list[i]['end_point'])].append(calculate_row_list[i])
        i=i+1
f.close()
calculate_row_csv_list = []
start_time = calculate_row_list[0]['time']
i=0
while i<len(calculate_row_list):
    calculate_row_list[i]['time'] = calculate_row_list[i]['time'] - start_time
    calculate_row_csv_list.append(dict([(value_unit_dict.get(key), value) for key, value in calculate_row_list[i].items()]))
    i=i+1
save_folder_name = input('enter save folder name: ')
parent_folder = os.path.join('results', save_folder_name)
parent_folder_exists = os.path.exists(parent_folder)
if not parent_folder_exists:
    os.mkdir(parent_folder)
with open(os.path.join(parent_folder,'result_values.csv'), 'w', encoding='utf8', newline='') as output_file:
    fc = csv.DictWriter(output_file,fieldnames=calculate_row_csv_list[0].keys())
    fc.writeheader()
    fc.writerows(calculate_row_csv_list)
output_file.close()
try:
    moving_point_color = (0,255,0)
    end_point_color = (255,0,0)
    for end_point in end_point_split_dict:
        save_img_array = np.zeros((x_range, y_range, 3), dtype = "uint8")
        i=0
        while i<len(end_point_split_dict[end_point]):
            if i!=len(end_point_split_dict[end_point])-1:
                line_start_point = (end_point_split_dict[end_point][i]['joystick_pos'][0]-calibrated_max_min["x_min"],end_point_split_dict[end_point][i]['joystick_pos'][1]-calibrated_max_min["x_min"])
                line_end_point = (end_point_split_dict[end_point][i+1]['joystick_pos'][0]-calibrated_max_min["x_min"],end_point_split_dict[end_point][i+1]['joystick_pos'][1]-calibrated_max_min["x_min"])
                save_img_array =cv2.line(save_img_array, line_start_point, line_end_point, color=moving_point_color, thickness=3)
            elif i==len(end_point_split_dict[end_point])-1:
                line_start_point = (end_point_split_dict[end_point][i]['joystick_pos'][0]-calibrated_max_min["x_min"],end_point_split_dict[end_point][i]['joystick_pos'][1]-calibrated_max_min["x_min"])
                line_end_point = (end_point_split_dict[end_point][0]['end_point'][0]-calibrated_max_min["x_min"],end_point_split_dict[end_point][0]['end_point'][1]-calibrated_max_min["x_min"])
                save_img_array =cv2.line(save_img_array, line_start_point, line_end_point, color=moving_point_color, thickness=3)
            i=i+1
        save_img_array =cv2.circle(save_img_array, (end_point_split_dict[end_point][0]['end_point'][0]-calibrated_max_min["x_min"],end_point_split_dict[end_point][0]['end_point'][1]-calibrated_max_min["x_min"]), radius=5, color=end_point_color, thickness=-1)
        save_frame = Image.fromarray(save_img_array)
        save_frame.save(os.path.join(parent_folder, str(end_point)+'.png'))
except Exception as e:
    print('error in saving images: '+str(e))
