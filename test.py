import os
import machine
import gc

PINS_TO_CHECK = list(range(0, 11)) + [20, 21]

def send_specs():
    specs = [
        "Versión MicroPython: {}".format(os.uname()),
        "Frecuencia CPU: {}".format(machine.freq()),
        "ID chip: {}".format(machine.unique_id()),
        "Memoria libre: {} bytes".format(gc.mem_free()),
        "Memoria total: {} bytes".format(gc.mem_alloc() + gc.mem_free())
    ]
    try:
        import network
        wlan = network.WLAN(network.STA_IF)
        specs.append("WiFi activo: {}".format(wlan.active()))
        specs.append("MAC WiFi: {}".format(wlan.config('mac')))
    except Exception:
        specs.append("WiFi: No disponible")
    try:
        import esp32
        specs.append("Temperatura interna: {}".format(esp32.raw_temperature()))
    except Exception:
        specs.append("Temperatura: No soportado")
    print("\n--- Especificaciones ---")
    for line in specs:
        print(line)
    print("\n--- Estado de pines (ESP32-C3 Super Mini) ---")
    for i in PINS_TO_CHECK:
        try:
            p = machine.Pin(i, machine.Pin.IN)
            print("GPIO", i, "valor:", p.value())
        except Exception:
            pass

send_specs()
