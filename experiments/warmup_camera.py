# The webcams need to "warmup"; it makes adjustments based on the exposure
# It does not need to be in the same script and the last exposure state persists over a period of time



import time
import subprocess

# Config
devices = ["/dev/video0", "/dev/video2", "/dev/video4"]
num_warmup_frames = 20
res_warmup = "480x270"

def warmup_camera(device):
    command = [
        "ffmpeg",
        "-loglevel", "error",
        "-f", "video4linux2",
        "-i", device,
        "-frames:v", str(num_warmup_frames),
        "-s", res_warmup,
        "-f", "null", "-"
    ]
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        print(f"Warm-up completed for {device}")
    except subprocess.TimeoutExpired:
        print(f"Warm-up timeout expired for {device}")
    except subprocess.CalledProcessError as e:
        print(f"Warm-up error with {device}: {e}")

def main():
    for device in devices:
        print(f"Starting warm-up for {device}...")
        warmup_camera(device)

if __name__ == "__main__":
    main()
