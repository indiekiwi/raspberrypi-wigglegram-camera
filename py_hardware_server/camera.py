import subprocess

class Camera:
    def warmup_camera(device):
        command = [
            "ffmpeg",
            "-loglevel", "error",
            "-f", "video4linux2",
            "-i", device,
            "-frames:v", "1",
            "-s", "480x270",
            "-vf", "lutrgb=r='val*1.1':g='val*0.95':b='val*0.9'",
            "-f", "null", "-"
        ]
        try:
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        except subprocess.TimeoutExpired:
            print(f"Warm-up timeout expired for {device}")
        except subprocess.CalledProcessError as e:
            print(f"Warm-up error with {device}: {e}")

    def capture_image(device, fragment, timestamp, image_dir):
        output_file = f"{image_dir}/{timestamp}_{fragment}.jpg"
        command = [
            "ffmpeg",
            "-loglevel", "error",
            "-f", "video4linux2",
            "-i", device,
            "-frames:v", "1",
            "-s", "1920x1080",
            "-vf", "lutrgb=r='val*1.1':g='val*0.95':b='val*0.9'",
            output_file
        ]
        try:
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        except subprocess.TimeoutExpired:
            print(f"Timeout expired for {device}")
        except subprocess.CalledProcessError as e:
            print(f"Error with {device}: {e}")
