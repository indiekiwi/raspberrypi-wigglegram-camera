import os
import subprocess
import time
import json
from multiprocessing import Pool
from gpiozero import Button, LED

# Configuration
devices = ["/dev/video0", "/dev/video2", "/dev/video4"]
fragments = ["A", "B", "C"]
image_dir = "images"
res = "1920x1080"
state_file = "state.json"
inactivity_shutdown_seconds = 300 # 5 mins
shutdown_hold_seconds = 3

button_shutter = Button(2)
button_secondary = Button(3)
led_flash = LED(17)    # white
led_status = LED(4)    # blue
led_error = LED(27)    # red
led_success = LED(22)  # green

os.makedirs(image_dir, exist_ok=True)

# Sync LEDs
def sync_leds():
    led_status.off()
    led_error.off()
    led_success.off()

# State management
def load_state():
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            return json.load(f)
    return {"flash": 1}

def save_state(state):
    with open(state_file, "w") as f:
        json.dump(state, f)

state = load_state()

# Capture Image
def capture_image(device, fragment, timestamp):
    output_file = f"{image_dir}/{timestamp}_{fragment}.jpg"
    command = [
        "ffmpeg",
        "-loglevel", "error",
        "-f", "video4linux2",
        "-i", device,
        "-frames:v", "1",
        "-s", res,
        output_file
    ]
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
    except subprocess.TimeoutExpired:
        print(f"Timeout expired for {device}")
    except subprocess.CalledProcessError as e:
        print(f"Error with {device}: {e}")

# Trigger shutdown of the pi
def shutdown():
    sync_leds()
    print("Shutting down the Raspberry Pi...")
    led_error.on()
    time.sleep(5)
    subprocess.run(["sudo", "shutdown", "-h", "now"])

# Flash toggle
def toggle_flash():
    state["flash"] = 1 - state["flash"]
    save_state(state)
    flash_state = "on" if state["flash"] else "off"
    print(f"Flash toggled {flash_state}")
    sync_leds()

# Main loop
def listen_for_buttons():
    i = 0
    inactivity = 0
    hold_start = None
    loop_delay = 0.1

    while True:
        inactivity = inactivity + loop_delay
        if inactivity > inactivity_shutdown_seconds:
            print(f"Trigged shutdown due to inactivity ({inactivity_shutdown_seconds} seconds)...")
            shutdown()

        if button_secondary.is_pressed:
            if not hold_start:
                hold_start = time.time()
            elif time.time() - hold_start >= shutdown_hold_seconds:
                shutdown()
            inactivity = 0
        else:
            if hold_start and time.time() - hold_start < shutdown_hold_seconds:
                toggle_flash()
            hold_start = None

        if button_shutter.is_pressed:
            print("Shutter button pressed...")
            timestamp = int(time.time())
            sync_leds()
            led_status.on()
            if state["flash"]:
                led_flash.on()
            with Pool(len(devices)) as pool:
                pool.starmap(capture_image, zip(devices, fragments, [timestamp] * len(devices)))
            sync_leds()
            led_flash.off()

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
            if len(captured_files) != len(fragments):
                led_error.blink(on_time=0.1, off_time=0.1, n=5, background=False)
                print(f"Error: Captured {len(captured_files)} instead of {len(fragments)}")
            else:
                led_success.blink(on_time=0.1, off_time=0.1, n=5, background=False)
            sync_leds()
            inactivity = 0
            print("ready...")

        i = (i + 1) % 10
        if i == 0:
            led_status.toggle()
            if state["flash"]:
                led_success.toggle()
            else:
                led_error.toggle()

        time.sleep(loop_delay)

if __name__ == "__main__":
    print("Started...")
    listen_for_buttons()
