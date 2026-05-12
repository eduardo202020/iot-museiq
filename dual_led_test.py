from machine import Pin
import time

LED_ONBOARD_GPIO = 8
LED_EXTERNAL_GPIO = 7

led_onboard = Pin(LED_ONBOARD_GPIO, Pin.OUT)
led_external = Pin(LED_EXTERNAL_GPIO, Pin.OUT)

print("Probando LEDs en GPIO{} y GPIO{}...".format(LED_ONBOARD_GPIO, LED_EXTERNAL_GPIO))

while True:
    led_onboard.value(1)
    led_external.value(1)
    print("LEDs ON")
    time.sleep(1)

    led_onboard.value(0)
    led_external.value(0)
    print("LEDs OFF")
    time.sleep(1)
