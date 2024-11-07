# raspberry-pi-wrigglegram

This project involves building and testing a Raspberry Pi setup with up to 4 USB webcams to simultaneously capture digital images, with the end goal of creating wigglegrams. The plan is to enclose the setup in a 3D-printed shell, investigate hardware limitations, and determine the minimum powered Raspberry Pi required to make it work. Once the setup is stable, the plan is to upgrade the webcams.

## Cameras Used
- 4 (very) old 0.3MP USB webcams.
- **ffmpeg** is used for capturing images from the webcams, instead of **libcamera**, which is typically used with the Raspberry Pi camera module.

## Raspberry Pi Models Tested
- **Raspberry Pi 2**: Unstable capture, with ~16,494ms delay using 3 cameras.
- **Raspberry Pi 3**: Unstable capture, with ~1,800ms delay using 3 cameras.
- **Raspberry Pi 400**: Stable capture, with ~1,200ms delay using 4 cameras.

