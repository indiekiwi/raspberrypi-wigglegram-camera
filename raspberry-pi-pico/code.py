import board
import digitalio
import usb_cdc
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import time

button_shutter = board.GP15

# Incoming Setup
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
if usb_cdc.console:
    print("Serial communication ready!")

# Outgoing Setup
button = digitalio.DigitalInOut(button_shutter)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP
keyboard = Keyboard(usb_hid.devices)

while True:
    # Incoming Loop (Serial)
    if usb_cdc.console.in_waiting > 0:
        signal = usb_cdc.console.read(1).decode('utf-8')
        if signal == "1":
            led.value = True
            usb_cdc.console.write(b"LED ON\n")
        elif signal == "0":
            led.value = False
            usb_cdc.console.write(b"LED OFF\n")

    # Outgoing Loop (Button pressed on the Pico)
    if not button.value:
        keyboard.press(Keycode.A)
    else:
        keyboard.release_all()

    time.sleep(0.1)
