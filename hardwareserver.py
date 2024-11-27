import os
import subprocess
import time
from multiprocessing import Pool
from gpiozero import Button, LED

# configuration
devices = ["/dev/video0", "/dev/video2", "/dev/video4"]
fragments = ["A", "B", "C"]
image_dir = "images"
resolutions = ["1920x1080", "960x540", "480x270"]
res = resolutions[0]

button_shutter = Button(2)
button_off = Button(3) # being connected to GPIO3 will also power on the pi when it's been shut down
led_flash = LED(17)
led_ready = LED(4)

os.makedirs(image_dir, exist_ok=True)

# button_shutter
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

# button_off
def shutdown():
    print("Shutting down the Raspberry Pi...")
    subprocess.run(["sudo", "shutdown", "-h", "now"])

# main loop
def listen_for_buttons():
    while True:
        if button_off.is_pressed:
            shutdown()
            break

        if button_shutter.is_pressed:
            print("Shutter button pressed...")
            timestamp = int(time.time())
            start_time = time.time()

            # Use multiprocessing Pool to run image capture in parallel
            led_flash.on()
            with Pool(len(devices)) as pool:
                pool.starmap(capture_image, zip(devices, fragments, [timestamp] * len(devices)))
            led_flash.off()

            # Logging captured files and timestamps
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
                print(f"Error: Captured {len(captured_files)} instead of {len(fragments)}")
            print("ready...")

        time.sleep(0.1)

if __name__ == "__main__":
    print("Started...")
    led_ready.on()
    listen_for_buttons()
