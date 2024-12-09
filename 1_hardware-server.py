import os
import subprocess
import time
import json
from multiprocessing import Pool
from gpiozero import Button, LED
from PIL import Image

# Preferences Config
num_warmup_frames = 3 # 5 seems optimal, @todo test usb 3.0 hub with 3x usb 3.0 ports could lower this as the usb 2.0 camera falls behind
shutdown_hold_seconds = 3
shutdown_inactivity_seconds = 900 # 15 mins
res = "1920x1080"
res_warmup = "480x270"
is_preview_landscape = 0
preview_factor = 4

# System Config
devices = ["/dev/video0", "/dev/video2", "/dev/video4"]
fragments = ["A", "B", "C"]
image_dir = "images"
state_file = "state.json"

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

def warmup_camera(device):
    command = [
        "ffmpeg",
        "-loglevel", "error",
        "-f", "video4linux2",
        "-i", device,
        "-frames:v", str(num_warmup_frames),
        "-s", res_warmup,
        "-vf", "lutrgb=r='val*1.1':g='val*0.95':b='val*0.9'",
        "-f", "null", "-"
    ]
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
    except subprocess.TimeoutExpired:
        print(f"Warm-up timeout expired for {device}")
    except subprocess.CalledProcessError as e:
        print(f"Warm-up error with {device}: {e}")

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
        "-vf", "lutrgb=r='val*1.1':g='val*0.95':b='val*0.9'",
        output_file
    ]
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
    except subprocess.TimeoutExpired:
        print(f"Timeout expired for {device}")
    except subprocess.CalledProcessError as e:
        print(f"Error with {device}: {e}")

def create_preview_image(image_paths, output_path):
    images = [Image.open(img_path) for img_path in image_paths]
    res_width, res_height = map(int, res.split('x'))

    if is_preview_landscape:
        preview_image = Image.new('RGB', (res_width * 3, res_height))
        x_offset = 0
        for img in images:
            preview_image.paste(img, (x_offset, 0))
            x_offset += img.width
    else:
        preview_image = Image.new('RGB', (res_width, res_height * 3))
        y_offset = 0
        for img in images:
            preview_image.paste(img, (0, y_offset))
            y_offset += img.height

    preview_image = preview_image.resize((int(preview_image.width / preview_factor), int(preview_image.height / preview_factor)))
    preview_image.save(output_path)
    print(f"Preview image saved at: {output_path}")

def send_via_bluetooth(image_path):
    config_file = "resources/config.env"

    # error handling
    if not os.path.isfile(config_file):
        print(f"[Bluetooth] No resources/config.env")
        return
    phone_mac_address = None
    with open(config_file, 'r') as f:
        for line in f:
            if line.startswith("PHONE_MAC_ADDRESS="):
                phone_mac_address = line.strip().split('=')[1]
                break
    if not phone_mac_address:
        print("[Bluetooth] PHONE_MAC_ADDRESS not found in resources/config.env")
        return
    if not os.path.isfile(image_path):
        print(f"[Bluetooth] Image not found: {image_path}")
        return
    try:
        result = subprocess.run(['bluetoothctl', 'info', phone_mac_address], capture_output=True, text=True)
        if "Device" in result.stdout:
            print(f"[Bluetooth] Device {phone_mac_address} is connected.")
        else:
            print(f"[Bluetooth] Device {phone_mac_address} is not connected. Skipping Bluetooth transfer.")
            return
    except Exception as e:
        print(f"[Bluetooth] Error checking connection: {e}")
        return

    # Use obexftp to send the image via Bluetooth
    try:
        subprocess.run([
            'obexftp', '--nopath', '--noconn', '--uuid', 'none', '--bluetooth', phone_mac_address,
            '--channel', '12', '--put', image_path
        ], check=True)
        print(f"[Bluetooth] Image sent to {phone_mac_address} successfully.")
    except subprocess.CalledProcessError as e:
        if e.stderr and "transfer complete" not in e.stderr.lower():
            print("Failed to send the image.")

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
                toggle_flash()
            hold_start = None

        # Shutter button logic
        if button_shutter.is_pressed:
            print("Shutter button pressed...")
            timestamp = int(time.time())

            sync_leds()
            led_status.on()

            with Pool(len(devices)) as pool:
                pool.starmap(warmup_camera, zip(devices))

            led_success.on()
            if state["flash"]:
                led_flash.on()
            with Pool(len(devices)) as pool:
                pool.starmap(capture_image, zip(devices, fragments, [timestamp] * len(devices)))
            led_error.on()
            time.sleep(0.5)

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
            expected_images = len(fragments)
            if len(captured_files) != expected_images:
                led_error.blink(on_time=0.1, off_time=0.1, n=5, background=False)
                print(f"Error: Captured {len(captured_files)} instead of {expected_images}")
            else:
                led_success.blink(on_time=0.1, off_time=0.1, n=5, background=False)
                print(f"Captured {expected_images}!")
                create_preview_image([f"images/{timestamp}_A.jpg", f"images/{timestamp}_B.jpg", f"images/{timestamp}_C.jpg"], f"images/preview_{timestamp}.jpg")
                send_via_bluetooth(f"images/preview_{timestamp}.jpg")
            sync_leds()
            inactivity = 0
            print("")
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
