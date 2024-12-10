import board
import digitalio
import usb_cdc

# Set up the onboard LED using board.LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# Ensure USB CDC is enabled
if usb_cdc.console:
    print("Serial communication ready!")

while True:
    if usb_cdc.console.in_waiting > 0:
        signal = usb_cdc.console.read(1).decode('utf-8')
        if signal == "1":
            led.value = True
            usb_cdc.console.write(b"LED ON\n")
        elif signal == "0":
            led.value = False
            usb_cdc.console.write(b"LED OFF\n")
