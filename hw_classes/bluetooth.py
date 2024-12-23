import os
import subprocess

class Bluetooth:
    def __init__(self):
        self.is_enable_bluetooth_transfer = True

    def toggle_preview(self):
        self.is_enable_bluetooth_transfer = not self.is_enable_bluetooth_transfer
        return self.is_enable_bluetooth_transfer

    def send_via_bluetooth(self, image_path):
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
