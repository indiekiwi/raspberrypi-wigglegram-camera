#!/bin/bash

# Identify the camera's and how they're mapped to eg. /dev/video0
echo "===== [1/2] Connected cameras ====="
v4l2-ctl --list-devices | grep -A 1 "CAM"
echo ""

# This lists the images, so we can check that all the fragment parts are captured as expected, as well as the capture time with ms to observe the delays between captures
echo "===== [2/2] Image info ====="
ls -lh --time-style=full-iso images/*jpg
echo ""
