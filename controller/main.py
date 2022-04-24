
from cmath import pi
import serial
import time
import threading
import queue
import numpy
import math

from os import listdir
from os.path import isfile, join

from svgpathtools import *



# initial angles after homing
HOME_Q1 = -17.000
HOME_Q2 = 142.511
FEED = 2000
PEN_DOWN = -5
PEN_UP = -30

 #"G10P0L20X0Y0Z0" - reset zero
            #"G0X107Y-142.511" - move to origin

HOME_COMMAND = "$H\r\nG10P0L20X"+str(HOME_Q1)+"Y"+str(HOME_Q2)+"Z0\r\n"

current_x = 0
current_y = 150

def raise_pen(ser):
    ser.write( ("G0Z" + str(PEN_UP) +"F1000\r\n").encode('utf8') )

def lower_pen(ser):
    ser.write( ("G0Z" + str(PEN_DOWN) +"F1000\r\n").encode('utf8') )

def inverse_kinematics(h,k):
    l1 = 200
    l2 = 120
    q2 = numpy.arccos( (h*h+k*k-l1*l1-l2*l2) / (2*l1*l2) )
    # q1 = numpy.arctan(k/h) - numpy.arctan( (l2*numpy.sin(q2)) / (l1 + l2*numpy.cos(q2)) )

    q1 = numpy.arctan2(k,h) - numpy.arctan2( l2*numpy.sin(q2) , l1 + l2*numpy.cos(q2) )

    # if (h<0):
    #     q1 = q1 + pi

    return [ numpy.rad2deg(q1), numpy.rad2deg(q2)]

def move_to(ser, x,y,z, feed):
    # global current_x, current_y

    q = inverse_kinematics(x,y)
    if (math.isnan(q[0]) or math.isnan(q[1])):
        print( "inverse kinematics failed" )
        return

    command = "G1X{:.2f}Y{:.2f}Z{:.2f}F{:.2f}\r\n".format(q[0],q[1],z,feed)
    print( command )
    ser.write( command.encode('utf8') )

    # num_steps = 10
    # dx = x-current_x
    # dy = y-current_y
    # for i in range(0,num_steps):
    #     nx = current_x + (i/num_steps) * dx
    #     ny = current_y + (i/num_steps) * dy
    #     q = inverse_kinematics(nx,ny)
    #     command = "G1X{:.2f}Y{:.2f}Z{:.2f}F{:.2f}\r\n".format(q[0],q[1],z,feed)
    #     print( command )
    #     ser.write( command.encode('utf8') )
        
    # q = inverse_kinematics(x,y)
    # command = "G1X{:.2f}Y{:.2f}Z{:.2f}F{:.2f}\r\n".format(q[0],q[1],z,feed)
    # print( command )
    # ser.write( command.encode('utf8') )

    # current_x = x
    # current_y = y
    # time.sleep(0.2)


def read_kbd_input(inputQueue):
    print('Ready for keyboard input:')
    while (True):
        input_str = input()
        inputQueue.put(input_str)

def main():
    global current_x, current_y

    files = [f for f in listdir("/dev") if f.startswith("tty.usbmodem")]
    ser = None
    command = None 

    if (len(files) > 0) :
        ser = serial.Serial(join("/dev",files[0]), 115200) # open serial port
    
    else :
        print("No serial port found")
        exit()

    if (ser is None):
        print("Unable to connect to serial port")
        exit()

    EXIT_COMMAND = "exit"
    inputQueue = queue.Queue()

    inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=True)
    inputThread.start()

    # time.sleep(2)
    
    hasSentInitialisation = False

    while (True):

        if (ser.inWaiting() > 0):
            # read the bytes and convert from binary array to ASCII
            data_str = ser.read(ser.inWaiting()).decode('ascii') 
            
            if (not data_str.startswith("ok")):
                print(data_str, end='') 

            if (not hasSentInitialisation): 
                hasSentInitialisation = True
                ser.write( HOME_COMMAND.encode('utf8') )
                raise_pen(ser)
                # move_to(ser, current_x, current_y, -15, 1000)

        if (inputQueue.qsize() > 0):
            input_str = inputQueue.get()

            if (input_str == EXIT_COMMAND):
                print("Exiting serial terminal.")
                break
            
            if (input_str == 'pic'):
                print_svg(ser,'pikachu.svg')
                # print_svg(ser,'cartman.svg')

            if (input_str == "sq"):
                move_to(ser, -50, 150, -15, FEED)
                move_to(ser, -50, 250, -15, FEED)
                move_to(ser, 50, 250, -15, FEED)
                move_to(ser, 50, 150, -15, FEED)

                move_to(ser, -60, 140, -15, FEED)
                move_to(ser, -60, 240, -15, FEED)
                move_to(ser, 60, 240, -15, FEED)
                move_to(ser, 60, 140, -15, FEED)

            ser.write( (input_str + "\r\n").encode('utf8') )

        time.sleep(0.01) 
    
    ser.close()
    print("End.")

def print_svg(ser, file):

        
        # doc = Document('pikachu.svg')
        # print(doc.bbox())
        # # for path in doc.paths():
        # #     # Do something with the transformed Path object.
        # #     foo(path)
        # #     # Inspect the raw SVG element, e.g. change its attributes
        # #     foo(path.element)
        # #     transform = result.transform
        # #     # Use the transform that was applied to the path.
        # #     foo(path.transform)
        # # foo(doc.tree)  # do stuff using ElementTree's functionality
        # doc.display()  # display doc in OS's default application
        # # doc.save('my_new_file.html')

    print("load SVG")
    paths, attributes = svg2paths(file)

    svg_xmin=9999999
    svg_xmax=-9999999
    svg_ymin=9999999
    svg_ymax=-9999999

    NUM_SAMPLES= 1000 # math.ceil(path.length() / segment_length)
    
    for path in paths:
    
        for i in range(NUM_SAMPLES):
            p = path.point(i/(float(NUM_SAMPLES)))
            
            x = p.real
            y = p.imag

            if (x>svg_xmax):
                svg_xmax=x 

            if (x<svg_xmin):
                svg_xmin=x 

            if (y>svg_ymax):
                svg_ymax=y

            if (y<svg_ymin):
                svg_ymin=y 
        
    svg_width = svg_xmax-svg_xmin
    svg_height = svg_ymax-svg_ymin 
    print( "SVG bbox:", svg_xmin, svg_xmax, svg_ymin, svg_ymax )
    
    PRINT_X_MIN = -50
    PRINT_X_MAX = 50
    PRINT_Y_MIN = 150
    PRINT_Y_MAX = 250
    PRINT_WIDTH = PRINT_X_MAX - PRINT_X_MIN
    PRINT_HEIGHT = PRINT_Y_MAX - PRINT_Y_MIN

    svg_aspect = svg_width/svg_height 
    print_aspect = PRINT_WIDTH/PRINT_HEIGHT 

    scale = 1
    offset_x = 0
    offset_y = 0

    print("Svg aspect", svg_aspect, "print aspect", print_aspect)

    if (svg_aspect>print_aspect):
        scale = PRINT_WIDTH/svg_width
        offset_x = 0
        offset_y = (PRINT_HEIGHT - (svg_height*scale)) / 2.0
    else:
        scale = PRINT_HEIGHT/svg_height
        offset_x = (PRINT_WIDTH - (svg_width*scale)) / 2.0
        print("scale", scale, "offset_x", offset_x)
        offset_y = 0


    
    
    print(NUM_SAMPLES)

    xmin=9999999
    xmax=-9999999
    ymin=9999999
    ymax=-9999999


    
    
    for path in paths:

        segment_length = 1
        NUM_SAMPLES= math.ceil(path.length() * scale / segment_length)
        raise_pen(ser);
        isPenUp = True 

        for i in range(NUM_SAMPLES):
            p = path.point(i/(float(NUM_SAMPLES)))
            
            x = (p.real-svg_xmin)*scale + offset_x + PRINT_X_MIN 
            y = (p.imag-svg_ymin)*scale + offset_y + PRINT_Y_MIN

            if (x>xmax):
                xmax=x 

            if (x<xmin):
                xmin=x 

            if (y>ymax):
                ymax=y

            if (y<ymin):
                ymin=y 
            
            print("{:.2f},{:.2f}".format(p.real, p.imag), "=>", "{:.2f},{:.2f}".format(x, y), )

            if (isPenUp):
                z = PEN_UP
            else:
                z = PEN_DOWN

            move_to(ser, x,y, z, FEED)

            if (i==0):
                lower_pen(ser)
                isPenUp = False

            time.sleep(0.05)
    
    width = xmax-xmin
    height = ymax-ymin 
    print( "iterate:", xmin, xmax, ymin, ymax, width, height )
    

if (__name__ == '__main__'): 
    main()
    # ser = "bob"
    # print_svg(ser, 'pikachu.svg')

# while (command != "exit"):
#     # Check if incoming bytes are waiting to be read from the serial input 
#     # buffer.
#     # NB: for PySerial v3.0 or later, use property `in_waiting` instead of
#     # function `inWaiting()` below!
#     if (ser.inWaiting() > 0):
#         # read the bytes and convert from binary array to ASCII
#         data_str = ser.read(ser.inWaiting()).decode('ascii') 
#         # print the incoming string without putting a new-line
#         # ('\n') automatically after every print()
#         print(data_str, end='') 

#     # Put the rest of your code you want here

    
#     command = input('>>\n')
#     if (command!="exit"):
#         ser.write( (command + "\n").encode('utf8') )

# #     print( ser.read_until() )
    
#     # Optional, but recommended: sleep 10 ms (0.01 sec) once per loop to let 
#     # other threads on your PC run during this time. 
#     time.sleep(0.01) 

# ser.write("\r\n\r\n".encode('utf8'))
# time.sleep(2)

# print("waiting...");

# ser.write("$$".encode('utf8'))

# s = ser.read(100)

# print("received...");
# print(s)


