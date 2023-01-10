#! /usr/bin/python
import serial           # import using pip
import time
import random

arduino = serial.Serial('COM7', 9600, timeout=0.1)

def check_reset(data):
    if 'reset' in data:
        return True
    return False

def generate_random_point(calibrated_max_min):
    random_points = []
    random_points.append(random.randint(calibrated_max_min["x_min"]+10,calibrated_max_min["x_max"]-10))
    random_points.append(random.randint(calibrated_max_min["y_min"]+10,calibrated_max_min["y_max"]-10))
    return random_points

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

print('spin joystick (maximum reach)')
write_read('1')

calibrated_max_min = {}
while True:
    rawdata = arduino.readline()
    data = str(rawdata.decode('utf-8'))
    print(data)
    if check_reset(data):
        break
    else:
        coordinates = get_coordinates(data)
        if "x_max" not in calibrated_max_min and coordinates[0]!=None:
            calibrated_max_min["x_max"] = coordinates[0]
        elif coordinates[0]!=None:
            if coordinates[0]>calibrated_max_min["x_max"]:
                calibrated_max_min["x_max"]=coordinates[0]
        if "x_min" not in calibrated_max_min and coordinates[0]!=None:
            calibrated_max_min["x_min"] = coordinates[0]
        elif coordinates[0]!=None: 
            if coordinates[0]<calibrated_max_min["x_min"]:
                calibrated_max_min["x_min"]=coordinates[0]
        if "y_max" not in calibrated_max_min and coordinates[1]!=None:
            calibrated_max_min["y_max"] = coordinates[1]
        elif coordinates[1]!=None:
            if coordinates[1]>calibrated_max_min["y_max"]:
                calibrated_max_min["y_max"]=coordinates[1]
        if "y_min" not in calibrated_max_min and coordinates[1]!=None:
            calibrated_max_min["y_min"] = coordinates[0]
        elif coordinates[1]!=None:
            if coordinates[1]<calibrated_max_min["y_min"]:
                calibrated_max_min["y_min"]=coordinates[1]
f=open("calibration_data.txt", "w")
f.write(str(calibrated_max_min))
f.close()
print("clibration complete!")
random_points = []
for x in range(0,100):
    random_points.append(generate_random_point(calibrated_max_min))
f=open("random_points.txt", "w")
f.write(str(random_points))
f.close()
print("created random points list!")
