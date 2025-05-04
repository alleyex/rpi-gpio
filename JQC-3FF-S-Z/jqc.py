class RelayModule:
    def __init__(self, pin):
        import RPi.GPIO as GPIO
        self.GPIO = GPIO
        self.pin = pin
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setup(self.pin, self.GPIO.OUT)

    def on(self):
        self.GPIO.output(self.pin, self.GPIO.HIGH)

    def off(self):
        self.GPIO.output(self.pin, self.GPIO.LOW)

    def cleanup(self):
        self.GPIO.cleanup()

if __name__ == '__main__':
    import time
    relay = RelayModule(17)  # GPIO 17
    try:
        print("繼電器啟動（開）")
        relay.on()
        time.sleep(5)
        print("繼電器關閉（斷）")
        relay.off()
        time.sleep(2)
    finally:
        relay.cleanup()
        print("GPIO清理完成")
