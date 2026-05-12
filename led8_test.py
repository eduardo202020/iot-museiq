from machine import Pin
import time

LED_GPIO = 8

led = Pin(LED_GPIO, Pin.OUT)

print("Probando LED integrado en GPIO{}...".format(LED_GPIO))

while True:
    led.value(1)
    print("GPIO{} ON".format(LED_GPIO))
    time.sleep(1)
    led.value(0)
    print("GPIO{} OFF".format(LED_GPIO))
    time.sleep(1)
