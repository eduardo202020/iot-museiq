from machine import Pin
from time import sleep, ticks_ms, ticks_diff

# LED integrado en GPIO2
led = Pin(2, Pin.OUT)

# Botón BOOT en GPIO0 (con pull-up, presionado = 0)
boton = Pin(0, Pin.IN, Pin.PULL_UP)

# Variables de control
led.value(0)  # LED apagado al inicio
inicial_delay = 1000  # Delay inicial en ms (1 segundo)
blink_delay = inicial_delay
min_delay = 50  # Delay mínimo en ms
delay_decrement = 100  # Cuánto disminuye el delay por cada pulsación
ultimo_tick = ticks_ms()
ultimo_estado_boton = 1  # 1 = no presionado

print("Presiona el botón BOOT para acelerar el parpadeo del LED")
print(f"Velocidad inicial: {blink_delay}ms")

while True:
    # Detectar pulsación del botón (flanco descendente)
    estado_boton = boton.value()
    if estado_boton == 0 and ultimo_estado_boton == 1:
        # Botón presionado
        if blink_delay > min_delay:
            blink_delay -= delay_decrement
            print(f"Velocidad aumentada: {blink_delay}ms")
        else:
            # Ya está en la velocidad máxima, reiniciar
            blink_delay = inicial_delay
            print(f"Reiniciado a velocidad inicial: {blink_delay}ms")
    ultimo_estado_boton = estado_boton
    
    # Controlar el parpadeo del LED
    if ticks_diff(ticks_ms(), ultimo_tick) >= blink_delay:
        led.value(not led.value())  # Alternar LED
        ultimo_tick = ticks_ms()
    
    sleep(0.01)  # Pequeña pausa para evitar lecturas excesivas
