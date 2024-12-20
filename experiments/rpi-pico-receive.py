import time
import RPi.GPIO as GPIO
import serial
from gpiozero import Button

ser = serial.Serial('/dev/ttyACM0', 9600)

ser.write(b'[1xf_lv]')
time.sleep(1)
ser.write(b'[0xf_lv]')
time.sleep(1)
