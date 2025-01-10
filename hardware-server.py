import os
import subprocess
import time
from multiprocessing import Pool
from gpiozero import Button

from hw_classes.led_controller import LEDController
from hw_classes.camera import Camera
from hw_classes.bluetooth import Bluetooth
from hw_classes.preview import Preview

# Preferences Config
hold_seconds = 3
shutdown_inactivity_seconds = 900 # 15 mins
is_debug = False

# System Config
devices = ["/dev/video4", "/dev/video2", "/dev/video0"]
fragments = ["A", "B", "C"]
image_dir = "images"

button_primary = Button(2)
button_secondary = Button(3)

led_controller = LEDController()
camera = Camera()
bluetooth = Bluetooth()
preview = Preview()

os.makedirs(image_dir, exist_ok=True)

# Trigger shutdown of the pi
def shutdown():
    led_controller.sync_leds()
    print("Shutting down the Raspberry Pi...")
    led_controller.turn_on_all()
    time.sleep(5)
    subprocess.run(["sudo", "shutdown", "-h", "now"])

# Main loop
def listen_for_buttons():
    i = 0
    inactivity = 0
    hold_start_primary = None
    hold_start_secondary = None
    loop_delay = 0.1

    while True:
        # Inactivity Management
        inactivity += loop_delay
        if inactivity > shutdown_inactivity_seconds:
            print(f"Triggered shutdown due to inactivity ({shutdown_inactivity_seconds} seconds)...")
            shutdown()

        # Primary button
        if button_primary.is_pressed:
            if not hold_start_primary:
                hold_start_primary = time.time()
            elif time.time() - hold_start_primary >= hold_seconds:
                primary_held()
                hold_start_primary = None
            inactivity = 0
        else:
            if hold_start_primary and time.time() - hold_start_primary < hold_seconds:
                primary_pressed()
                inactivity = 0;
            hold_start_primary = None

        # Secondary button
        if button_secondary.is_pressed:
            if not hold_start_secondary:
                hold_start_secondary = time.time()
            elif time.time() - hold_start_secondary >= hold_seconds:
                secondary_held()
                hold_start_secondary = None
            inactivity = 0
        else:
            if hold_start_secondary and time.time() - hold_start_secondary < hold_seconds:
                secondary_pressed()
            hold_start_secondary = None

        i = (i + 1) % 10
        if i == 0:
            led_controller.toggle_blue()
        elif i == 5:
            if bluetooth.is_enable_bluetooth_transfer:
                led_controller.toggle_green()

        time.sleep(loop_delay)

def primary_pressed():
    print("Primary Pressed (Take Photo)")
    timestamp = int(time.time())

    led_controller.turn_on_blue()
    led_controller.turn_on_green()
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
        led_controller.blink_white()
        print(f"Error: Captured {len(captured_files)} instead of {expected_images}")
    else:
        led_controller.blink_green()
        print(f"Captured {expected_images}!")
        if not bluetooth.is_enable_bluetooth_transfer:
            print("[Bluetooth] Transfer is disabled")
        else:
            handle_preview(timestamp)
    led_controller.sync_leds()
    print("")
    print("ready...")

def primary_held():
    led_controller.turn_on_blue()
    led_controller.turn_on_green(True)
    is_preview = bluetooth.toggle_preview()
    print("Preview turned on" if is_preview else "Preview turned off")
    time.sleep(2)
    led_controller.sync_leds()

def secondary_pressed():
    print("Secondary Pressed (Warmup Camera)")
    led_controller.turn_on_white()
    with Pool(len(devices)) as pool:
        pool.starmap(Camera.warmup_camera, zip(devices))
    print("Warmed up!")
    led_controller.sync_leds()

def secondary_held():
    print("Secondary Held (Shutdown)")
    led_controller.turn_on_blue()
    led_controller.turn_on_white(True)
    time.sleep(2)
    led_controller.sync_leds()
    if is_debug:
        print("Shutdown (Not actually shutting down in debug mode)")
    else:
        shutdown()

def handle_preview(timestamp):
    preview.create_preview_image(
        [f"images/{timestamp}_A.jpg", f"images/{timestamp}_B.jpg", f"images/{timestamp}_C.jpg"],
        f"images/preview_{timestamp}.jpg"
    )
    bluetooth.send_via_bluetooth(f"images/preview_{timestamp}.jpg")

if __name__ == "__main__":
    print("Started...")
    listen_for_buttons()
