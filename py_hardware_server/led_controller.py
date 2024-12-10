from gpiozero import LED

class LEDController:
    def __init__(self):
        # Initialize the LEDs
        self.led_status = LED(4)
        self.led_error = LED(27)
        self.led_success = LED(22)
        self.led_flash = LED(17)
        self.leds = [self.led_status, self.led_error, self.led_success, self.led_flash]

    def sync_leds(self):
        """Turn off all LEDs."""
        for led in self.leds:
            led.off()

    def turn_on_success(self):
        """Turn on success LED."""
        self.sync_leds()
        self.led_success.on()

    def blink_success(self):
        self.led_success.blink(on_time=0.1, off_time=0.1, n=5, background=False)

    def toggle_success(self):
        self.led_success.toggle()

    def turn_on_error(self):
        """Turn on error LED."""
        self.sync_leds()
        self.led_error.on()

    def blink_error(self):
        self.led_error.blink(on_time=0.1, off_time=0.1, n=5, background=False)

    def toggle_error(self):
        self.led_error.toggle()

    def turn_on_status(self):
        """Toggle the status LED."""
        self.sync_leds()
        self.led_status.on()

    def toggle_status(self):
        self.led_status.toggle()

    def turn_on_flash(self):
        """Toggle the flash LED."""
        self.led_flash.on()

    def turn_on_all(self):
        """Turn on all except flash"""
        self.led_success.on()
        self.led_error.on()
        self.led_status.on()
        self.led_flash.off()
