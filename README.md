# robot-nerf

This project is a Nerf gun attached to a partially built SCARA robot arm.  Using pose tracking, the gun will aim and open fire if you don't put your hands up!

## Overview

The robot arm is built from a combination of steel-tube and 3D printed parts, with motion provided by stepper motors.  Control comes in the form of an Arduino Uno with CNC shield.  The X-axis is configured on the arm to rotate about the main axis, and the Nerf gun is attached to this axis. This means the X-axis of the arm directly controls the angle of the gun.

<img src="https://user-images.githubusercontent.com/3776113/112767045-6e54f180-900c-11eb-9ec9-494e055ae296.png" height="250">


## Ardino Code

The arm is controlled via an Ardiuno Uno with a CNC shield. In this project, only the X-axis of the arm is controlled. The Arduino sketch in the /stepper folder takes an angle input via serial input, and moves the arm to this angle.

## Tracking

To track the person, a webcam on a laptop is used, placed underneath the arm, such that the center of rotation of the arm is directly in line with the webcam.  This makes the position of the person in the webcam directly proportional to the angle of the gun.

<img src="https://user-images.githubusercontent.com/3776113/112767561-47e48580-900f-11eb-9c70-695c82ba5b9f.png" height="300">

The tracking is done with software written in Python using the Google MediaPipe library : https://google.github.io/mediapipe/solutions/pose.html.  This library automatically detects and tracks the pose of a person who can be seen by the webcam.

The MediaPipe library detects the location of landmarks on the person being tracked:

<img src="https://user-images.githubusercontent.com/3776113/112766338-42843c80-9009-11eb-99ec-d2a5285a549e.png" height="300">

To obtain the location of the person, the average x-position of all the detected landmarks is used. The landmarks are referenced from 0 on the left of the screen to 1 on the right.  A simple calculation is used to convert this to an angle:

`angle = (x-0.5) * FOV`

FOV is the field of view of the camera, which in this case is a MacBook pro webcam, and through trial-and-error a value of 80 works well.

To detect if the person is holding their hands up, a check is done to see if landmark 15 is above landmark 11, and 16 is above 12.

