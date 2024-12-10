import os
import subprocess
import time
import serial
from multiprocessing import Pool
from gpiozero import Button

from hw_classes.led_controller import LEDController
from hw_classes.camera import Camera
from hw_classes.flash import Flash
from hw_classes.bluetooth import Bluetooth
from hw_classes.preview import Preview

# Preferences Config
shutdown_hold_seconds = 3
shutdown_inactivity_seconds = 9001 # 15 mins

# System Config
devices = ["/dev/video0", "/dev/video2", "/dev/video4"]
fragments = ["A", "B", "C"]
image_dir = "images"

button_shutter = Button(2)
button_secondary = Button(3)

led_controller = LEDController()
camera = Camera()
flash = Flash()
bluetooth = Bluetooth()
preview = Preview()

os.makedirs(image_dir, exist_ok=True)

# Trigger shutdown of the pi
def shutdown():
    led_controller.sync_leds()
    print("Shutting down the Raspberry Pi...")
    led_controller.turn_on_error()
    time.sleep(5)
    subprocess.run(["sudo", "shutdown", "-h", "now"])

# Main loop
def listen_for_buttons():
    i = 0
    inactivity = 0
    hold_start = None
    loop_delay = 0.1

    while True:
        inactivity += loop_delay
        if inactivity > shutdown_inactivity_seconds:
            print(f"Triggered shutdown due to inactivity ({shutdown_inactivity_seconds} seconds)...")
            shutdown()

        # Secondary button logic (shutdown or flash toggle)
        if button_secondary.is_pressed:
            if not hold_start:
                hold_start = time.time()
            elif time.time() - hold_start >= shutdown_hold_seconds:
                shutdown()
            inactivity = 0
        else:
            if hold_start and time.time() - hold_start < shutdown_hold_seconds:
                flash.toggle()
                led_controller.sync_leds()
            hold_start = None

        # Shutter button logic
        if button_shutter.is_pressed:
            print("Shutter button pressed...")
            timestamp = int(time.time())

            led_controller.turn_on_status()

            ser = serial.Serial('/dev/ttyACM0', 9600)
            ser.write(b'1')

# @todo: Move to a seperate button
#            with Pool(len(devices)) as pool:
#                pool.starmap(warmup_camera, zip(devices))

            led_controller.turn_on_success()
            if flash.is_on():
                led_controller.turn_on_flash()
            with Pool(len(devices)) as pool:
                pool.starmap(Camera.capture_image, zip(devices, fragments, [timestamp] * len(devices), [image_dir] * len(devices)))
            time.sleep(0.5)
            led_controller.sync_leds()

            captured_files = [
                f for f in os.listdir(image_dir)
                if f.startswith(f"{timestamp}_")
            ]
            captured_files.sort()

            file_timestamps = []
            for file, fragment in zip(captured_files, fragments):
                filepath = os.path.join(image_dir, file)
                file_time_us = int(os.path.getmtime(filepath) * 1_000_000)
                file_timestamps.append((fragment, file_time_us))

            file_timestamps.sort(key=lambda x: x[1])
            base_time_us = file_timestamps[0][1]

            for i, (fragment, file_time_us) in enumerate(file_timestamps):
                time_diff_ms = (file_time_us - base_time_us) // 1_000
                diff_text = f"+{time_diff_ms}ms" if i > 0 else "+0ms"
                print(f"{fragment} {diff_text}")

            # Error handling if fewer files are captured than expected
            expected_images = len(fragments)
            if len(captured_files) != expected_images:
                led_controller.blink_error()
                print(f"Error: Captured {len(captured_files)} instead of {expected_images}")
            else:
                led_controller.blink_success()
                print(f"Captured {expected_images}!")
                preview.create_preview_image([f"images/{timestamp}_A.jpg", f"images/{timestamp}_B.jpg", f"images/{timestamp}_C.jpg"], f"images/preview_{timestamp}.jpg")
                bluetooth.send_via_bluetooth(f"images/preview_{timestamp}.jpg")
            led_controller.sync_leds()
            inactivity = 0
            ser.write(b'0')
            print("")
            print("ready...")

        i = (i + 1) % 10
        if i == 0:
            led_controller.toggle_status()
            if flash.is_on():
                led_controller.toggle_success()
            else:
                led_controller.toggle_error()

        time.sleep(loop_delay)

if __name__ == "__main__":
    print("Started...")
    listen_for_buttons()
