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
    print(type(reader))
    for row in reader:
        converted_dict = {'time': ast.literal_eval(row['time']), 'joystick_pos': ast.literal_eval(row['joystick_pos']), 'start_point': ast.literal_eval(row['start_point']), 'end_point': ast.literal_eval(row['end_point']), 'mode': row['mode']}
        calculate_row_list.append(converted_dict)
    print('csv length: '+str(len(calculate_row_list)))
    i=0
    while i<len(calculate_row_list):
        if 'velocity' not in calculate_row_list[i] and i!=len(calculate_row_list)-1:
            time_diff = calculate_row_list[i+1]['time']- calculate_row_list[i]['time']
            distance = math.dist(calculate_row_list[i+1]['joystick_pos'],calculate_row_list[i]['joystick_pos'])
            calculate_row_list[i]['velocity'] = distance/time_diff
        elif 'velocity' not in calculate_row_list[i] and i==len(calculate_row_list)-1:
            calculate_row_list[i]['velocity'] = 0
        i=i+1
    i=0
    while i<len(calculate_row_list):
        if 'acceleration' not in calculate_row_list[i] and i!=len(calculate_row_list)-1:
            time_diff = calculate_row_list[i+1]['time']- calculate_row_list[i]['time']
            velocity_diff = calculate_row_list[i+1]['velocity'] - calculate_row_list[i]['velocity']
            calculate_row_list[i]['acceleration'] = velocity_diff/time_diff
        elif 'acceleration' not in calculate_row_list[i] and i==len(calculate_row_list)-1:
            calculate_row_list[i]['acceleration'] = 0
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
save_folder_name = input('enter save folder name: ')
parent_folder = os.path.join('results', save_folder_name)
parent_folder_exists = os.path.exists(parent_folder)
if not parent_folder_exists:
    os.mkdir(parent_folder)
with open(os.path.join(parent_folder,'result_values.csv'), 'w', encoding='utf8', newline='') as output_file:
    fc = csv.DictWriter(output_file,fieldnames=calculate_row_list[0].keys())
    fc.writeheader()
    fc.writerows(calculate_row_list)
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
