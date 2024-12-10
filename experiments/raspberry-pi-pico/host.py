import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import time

button = digitalio.DigitalInOut(board.GP15)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

keyboard = Keyboard(usb_hid.devices)

while True:
    if not button.value:
        keyboard.press(Keycode.A)
    else:
        keyboard.release_all()

    time.sleep(0.1)
