import time
import RPi.GPIO as GPIO
import serial
from gpiozero import Button

# Setup GPIO 2 for button input
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button connected to GPIO 2
button_shutter = Button(2)

# Set up serial communication with Raspberry Pi Pico (via USB serial)
ser = serial.Serial('/dev/ttyACM0', 9600)  # Adjust to your Pico's serial port (it might be /dev/ttyACM0 or another port)

# Button press detection
try:
    while True:
#        if GPIO.input(2) == GPIO.LOW:  # Button is pressed (active low)
        if button_shutter.is_pressed:
            print("Button Pressed on Pi 4 - Sending signal to Pico to turn on LED.")
            ser.write(b'1')  # Send 'ON' signal to Pico to light up LED
            time.sleep(0.2)  # Debounce delay
        else:
            ser.write(b'0')
            time.sleep(0.1)  # Button is not pressed, wait
except KeyboardInterrupt:
    print("Program terminated.")
    GPIO.cleanup()
    ser.close()
