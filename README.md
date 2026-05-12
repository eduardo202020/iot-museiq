# iot-museiq

Proyecto de pruebas BLE con ESP32/ESP32-C3 (MicroPython), dividido en dos scripts:

- `museiq.py`: beacon BLE para identificacion/zonas.
- `testApp/bidir.py`: comunicacion BLE bidireccional con la app (comandos, LEDs y boton).

## Estructura

- `museiq.py`: beacon conectable con advertising y datos de sala.
- `flujo.md`: flujo rapido para cargar/probar `museiq.py`.
- `testApp/bidir.py`: servicio BLE con RX/TX para interaccion con app.
- `testApp/flujo.md`: flujo rapido de prueba para `testApp`.

## Requisitos

- ESP32 con MicroPython.
- Si usas `ESP32-C3 Super Mini`, revisa y ajusta los GPIO de `testApp/bidir.py` antes de cargarlo.
- Python en PC + entorno virtual (`.venv`).
- `mpremote` instalado en el entorno virtual.

## Arranque rapido

**Activar entorno virtual:**

```bash
cd ~/proyectos/iot/museiq/iot-museiq
source .venv/bin/activate
```

**Ver el puerto del mini conectado por cable de datos:**

```bash
ls -l /dev/ttyACM*
```

En tus pruebas el puerto usado fue `"/dev/ttyACM0"`.

## Comandos Listos

**Cargar `S1-M1`:**

```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 fs cp testApp/mini_1.py :main.py
.venv/bin/python -m mpremote connect /dev/ttyACM0 reset
```

**Cargar `S1-M2`:**

```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 fs cp testApp/mini_2.py :main.py
.venv/bin/python -m mpremote connect /dev/ttyACM0 reset
```

**Cargar `S1-M3`:**

```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 fs cp testApp/mini_3.py :main.py
.venv/bin/python -m mpremote connect /dev/ttyACM0 reset
```

**Abrir REPL / ver logs:**

```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 repl
```

_(Salir con `Ctrl+]` o `Ctrl+x`)_

**Encender LED integrado (`GPIO8`) desde terminal:**

```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 exec "from machine import Pin; Pin(8, Pin.OUT).value(1)"
```

**Apagar LED integrado (`GPIO8`) desde terminal:**

```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 exec "from machine import Pin; Pin(8, Pin.OUT).value(0)"
```

**Encender LED externo (`GPIO7`) desde terminal:**

```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 exec "from machine import Pin; Pin(7, Pin.OUT).value(1)"
```

**Apagar LED externo (`GPIO7`) desde terminal:**

```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 exec "from machine import Pin; Pin(7, Pin.OUT).value(0)"
```

**Iniciar prueba de ambos LEDs parpadeando:**

```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 fs cp dual_led_test.py :main.py
.venv/bin/python -m mpremote connect /dev/ttyACM0 reset
```

**Instalar `mpremote` si hace falta:**

```bash
.venv/bin/python -m pip install mpremote
```

## BLE en testApp

Configuracion actual para `ESP32-C3 Super Mini` en `testApp/bidir.py`:

- Nombre BLE: `ESP32-C3-Bidir`
- `LED1_GPIO = 8` (comunmente el LED integrado)
- `LED2_GPIO = 7` (LED externo recomendado para tu placa)
- `BUTTON_GPIO = None` (deshabilitado por defecto)

Si tu placa usa otro pin para el LED integrado, cambia `LED1_GPIO`. En muchas variantes del `ESP32-C3 Super Mini` el LED integrado esta en `GPIO8`, pero puede variar segun el fabricante.

Perfiles listos para 3 minis:

- `testApp/mini_1.py` anuncia `S1-M1` y expone `S1|M1` al conectar
- `testApp/mini_2.py` anuncia `S1-M2` y expone `S1|M2` al conectar
- `testApp/mini_3.py` anuncia `S1-M3` y expone `S1|M3` al conectar

Ademas, estos perfiles anuncian `TX_POWER_DBM = -12` en el advertising BLE y lo exponen al conectar como:

- `S1|M1|TX=-12`
- `S1|M2|TX=-12`
- `S1|M3|TX=-12`

Para cargar uno especifico:

```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 fs cp testApp/mini_1.py :main.py
.venv/bin/python -m mpremote connect /dev/ttyACM0 reset
```

Servicio y caracteristicas:

- Servicio: `0xA100`
- RX (app -> ESP32): `0xA101` (`WRITE`, `WRITE_NO_RESPONSE`)
- TX (ESP32 -> app): `0xA102` (`READ`, `NOTIFY`)

## Comandos que recibe el ESP32 (RX)

- `LED1_ON` / `LED1_OFF`
- `LED2_ON` / `LED2_OFF`
- Compatibilidad: `LED_PIN36_ON` / `LED_PIN36_OFF` (redirige a LED1)

## Respuestas/eventos que envia el ESP32 (TX)

- Confirmaciones LED:
  - `LED1_GPIO8_ON` / `LED1_GPIO8_OFF` si mantienes la configuracion por defecto
  - `LED2_GPIO7_ON` / `LED2_GPIO7_OFF` si mantienes la configuracion por defecto
- Evento boton:
  - `BOTON_GPIOx_PRESS`
  - `BOTON_GPIOx_RELEASE`

Nota: la app debe suscribirse a notificaciones en `0xA102` para recibir eventos espontaneos (como boton).

## Mapa de pines usado en testApp

- LED1: `GPIO8` por defecto en `ESP32-C3 Super Mini`
- LED2: `GPIO7` por defecto para LED externo
- Boton: deshabilitado por defecto; define un GPIO externo con `PULL_UP` si lo necesitas

Importante: en `ESP32-C3` los pines de strapping pueden variar segun la placa. Evita usar pines de arranque para botones si no has verificado el pinout exacto de tu modulo.

## Envio manual desde terminal (sin REPL interactivo)

```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 exec "import main; main.send_text('Hola desde teclado')"
```
