# Sending a signal from a raspberry pi pico microcontroller and controlling gpio on the raspberry pi 4

import time
import RPi.GPIO as GPIO
import glob
from evdev import InputDevice, categorize, ecodes

GPIO_LED_TEST = 17 # White

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_LED_TEST, GPIO.OUT)

device_paths = glob.glob('/dev/input/by-id/usb-Raspberry_Pi_Pico_*event-kbd')
if not device_paths:
    print("No Raspberry Pi Pico HID device found!")
    exit(1)

device_path = device_paths[0]
dev = InputDevice(device_path)

print(f"Listening to events from: {dev}")

try:
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            key_event = categorize(event)
            if key_event.keystate == 1:
                print("Button on Pico pressed")
                GPIO.output(GPIO_LED_TEST, GPIO.HIGH)
            elif key_event.keystate == 0:
                print("Button on Pico released")
                GPIO.output(GPIO_LED_TEST, GPIO.LOW)

except KeyboardInterrupt:
    GPIO.cleanup()
