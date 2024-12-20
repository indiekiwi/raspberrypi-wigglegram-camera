from gpiozero import LED

class LEDController:
    def __init__(self):
        # Initialize the LEDs
        self.led_blue = LED(27)
        self.led_white = LED(17)
        self.led_green = LED(22)
        self.leds = [self.led_blue, self.led_white, self.led_green]

    def sync_leds(self):
        """Turn off all LEDs."""
        for led in self.leds:
            led.off()

    def turn_on_green(self):
        """Turn on green LED."""
        self.sync_leds()
        self.led_green.on()

    def blink_green(self):
        self.led_green.blink(on_time=0.1, off_time=0.1, n=5, background=False)

    def toggle_green(self):
        self.led_green.toggle()

    def turn_on_white(self):
        """Turn on white LED."""
        self.sync_leds()
        self.led_white.on()

    def blink_white(self):
        self.led_white.blink(on_time=0.1, off_time=0.1, n=5, background=False)

    def toggle_white(self):
        self.led_white.toggle()

    def turn_on_blue(self):
        """Toggle the blue LED."""
        self.sync_leds()
        self.led_blue.on()

    def toggle_blue(self):
        self.led_blue.toggle()

    def turn_on_all(self):
        """Turn on all except flash"""
        self.led_green.on()
        self.led_white.on()
        self.led_blue.on()
