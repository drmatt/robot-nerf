import cv2
import serial
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

from os import listdir
from os.path import isfile, join
files = [f for f in listdir("/dev") if f.startswith("tty.usbmodem")]

print( files, len(files) )
ser = None

if (len(files) > 0) :
  ser = serial.Serial(join("/dev",files[0])) # open serial port
  
else :
  print("No serial port found")


     # write a string

# For webcam input:
cap = cv2.VideoCapture(0)
  
with mp_pose.Pose( min_detection_confidence=0.5,
  min_tracking_confidence=0.5) as pose:
  while cap.isOpened():

    print("Here")

    success, image = cap.read()
    
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # Flip the image horizontally for a later selfie-view display, and convert
    # the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    results = pose.process(image)

    # Draw the pose annotation on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    mp_drawing.draw_landmarks(
        image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    

    if (ser is not None and results.pose_landmarks is not None) :
        x = 0
        y = 0
        n = 0
        for landmark in results.pose_landmarks.landmark:
            if landmark.visibility > 0.5:
                x += landmark.x
                y += landmark.y
                n += 1

        landmarks = results.pose_landmarks.landmark
        
        if (landmarks[15].visibility > 0.5 and  
            landmarks[11].visibility > 0.5 and  
            landmarks[16].visibility > 0.5 and 
            landmarks[12].visibility > 0.5) :

            ser.write( ("g1\n").encode('utf8') )

            if (landmarks[15].y > landmarks[11].y and 
                landmarks[16].y > landmarks[12].y) :

              ser.write( ("t1\n").encode('utf8') )
            else:
              ser.write( ("t0\n").encode('utf8') )

        else:
            ser.write( ("g0\n").encode('utf8') )
            ser.write( ("t0\n").encode('utf8') )

        if n>0 :
            x /= n 
            y /= n 
            print( x, ",", y )
            angle = (x-0.5) * 80
            
            ser.write( (str(angle) + "\n").encode('utf8') )

    
    cv2.imshow('MediaPipe Pose', image)
    
    if cv2.waitKey(5) & 0xFF == 27:
      break

cap.release()
ser.close()
