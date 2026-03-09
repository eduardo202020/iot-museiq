# iot-museiq

Proyecto de pruebas BLE con ESP32 (MicroPython), dividido en dos scripts:

- `museiq.py`: beacon BLE para identificacion/zonas.
- `testApp/bidir.py`: comunicacion BLE bidireccional con la app (comandos, LEDs y boton).

## Estructura

- `museiq.py`: beacon conectable con advertising y datos de sala.
- `flujo.md`: flujo rapido para cargar/probar `museiq.py`.
- `testApp/bidir.py`: servicio BLE con RX/TX para interaccion con app.
- `testApp/flujo.md`: flujo rapido de prueba para `testApp`.

## Requisitos

- ESP32 con MicroPython.
- Python en PC + entorno virtual (`.venv`).
- `mpremote` instalado en el entorno virtual.

Comando de instalacion:

```powershell
.\.venv\Scripts\python.exe -m pip install mpremote
```

## Flujo Base (museiq beacon)

Cargar y resetear:

```powershell
.\.venv\Scripts\python.exe -m mpremote connect COM5 fs cp museiq.py :main.py
.\.venv\Scripts\python.exe -m mpremote connect COM5 reset
```

Ver logs:

```powershell
.\.venv\Scripts\python.exe -m mpremote connect COM5 repl
```

## Flujo TestApp (BLE bidireccional)

Cargar y resetear:

```powershell
.\.venv\Scripts\python.exe -m mpremote connect COM5 fs cp testApp\bidir.py :main.py
.\.venv\Scripts\python.exe -m mpremote connect COM5 reset
```

Ver logs:

```powershell
.\.venv\Scripts\python.exe -m mpremote connect COM5 repl
```

## BLE en testApp

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
  - `LED1_GPIO2_ON` / `LED1_GPIO2_OFF`
  - `LED2_GPIO15_ON` / `LED2_GPIO15_OFF`
- Evento boton:
  - `BOTON_GPIO0_PRESS`
  - `BOTON_GPIO0_RELEASE`

Nota: la app debe suscribirse a notificaciones en `0xA102` para recibir eventos espontaneos (como boton).

## Mapa de pines usado en testApp

- LED1: `GPIO2`
- LED2: `GPIO15`
- Boton: `GPIO0` con `PULL_UP` (activo en LOW)

Importante: `GPIO0` es pin de arranque del ESP32. Evita mantener el boton presionado durante reset para no entrar en modo bootloader.

## Envio manual desde terminal (sin REPL interactivo)

```powershell
.\.venv\Scripts\python.exe -m mpremote connect COM5 exec "import main; main.send_text('Hola desde teclado')"
```

## Git (commits ya hechos)

Se organizaron cambios en dos commits:

- `refactor: rename main.py to museiq.py and update workflow docs`
- `feat(testApp): add bidirectional BLE app with LED and button events`
