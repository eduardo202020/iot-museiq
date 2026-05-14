# iot-museiq

Proyecto de pruebas BLE con ESP32/ESP32-C3 (MicroPython), dividido en dos aplicaciones:

- **`museiq.py`**: beacon BLE para identificación/zonas (solo advertising, opcional connectable).
- **`testApp/bidir.py`**: servicio BLE bidireccional con RX/TX para interacción con app (control de LEDs, botones, comandos).
- **`testApp/mini_1.py`, `mini_2.py`, `mini_3.py`**: versiones preconfigradas para salas/dispositivos específicos.

## Características

### Beacon BLE (`museiq.py`)
- **Advertising beacon conectable** con datos de sala y dispositivo
- **Service Data (UUID `0xA00A`)** con estructura de 12 bytes:
  - `ROOM_ID` (6 bytes UTF-8): Identificador de sala (ej. `"SALA_1"`)
  - `BEACON_NODE` (1 byte): Número del beacon en la sala (1-255)
  - `FW_VERSION` (2 bytes): Major + Minor (ej. `0x01 0x00` para v1.0)
  - `TX_POWER_DBM` (1 byte signed): Potencia de TX calibrada (-128 a 127 dBm)
  - `BATTERY_MV` (2 bytes): Nivel de batería en mV (0-65535)
- **Intervalo de advertising**: 500 ms (configurable)
- **Potencia TX**: -12 dBm (distancias cortas) o -4 dBm (distancias largas 4-10m)
- **GATTS Characteristics**:
  - `0xA00B` (READ): Beacon ID (ej. `"SALA_1-B02"`)
  - `0xA00C` (READ): TX Power DBM

### Servicio Bidireccional (`testApp/bidir.py`)
- **Comunicación BLE full-duplex** (RX/TX)
- **Service UUID**: `0xA100`
- **Characteristics**:
  - `0xA101` (WRITE/WRITE_NO_RESPONSE): RX desde app → ESP32
  - `0xA102` (READ/NOTIFY): TX desde ESP32 → app
- **Encoding**: UTF-8 (con fallback a hex si no decodable)
- **Comandos soportados**:
  - `LED1_ON` / `LED1_OFF`: Control LED1 (GPIO8)
  - `LED2_ON` / `LED2_OFF`: Control LED2 (GPIO7)
  - `LED_PIN36_ON` / `LED_PIN36_OFF`: Compatibilidad con comandos legacy
- **Respuestas**: Formato `"LED{N}_GPIO{pin}_{ON|OFF}"` o error
- **Device Name**: Configurable (ej. `"ESP32-C3-Bidir"` o `"S1-M1"`)

### Variantes Preconfigradas
- **`testApp/mini_1.py`**: `S1-M1` (Sala 1, Mini 1)
- **`testApp/mini_2.py`**: `S1-M2` (Sala 1, Mini 2)
- **`testApp/mini_3.py`**: `S1-M3` (Sala 1, Mini 3)

Cada una incluye códigos de sala/dispositivo en el device name y puede customizarse en variables de configuración.

## Estructura

```
.
├── museiq.py                 # Beacon BLE conectable
├── testApp/
│   ├── bidir.py              # Servicio bidireccional genérico
│   ├── mini_1.py             # Preconfigrado S1-M1
│   ├── mini_2.py             # Preconfigrado S1-M2
│   ├── mini_3.py             # Preconfigrado S1-M3
│   └── flujo.md              # Flujo de prueba
├── dual_led_test.py          # Test de ambos LEDs alternando
├── led7_test.py              # Test GPIO7 (LED externo)
├── led8_test.py              # Test GPIO8 (LED integrado)
├── test.py                   # Pruebas generales
├── flujo.md                  # Flujo rápido museiq.py
├── chat.md                   # Notas de desarrollo
└── firmware/                 # Posibles binarios de firmware

```

## Requisitos

- **Hardware**: ESP32 o ESP32-C3 Super Mini con MicroPython
- **Software en PC**: Python 3.6+ + entorno virtual (`.venv`)
- **Herramientas**: `mpremote` (incluido en `.venv`)
- **GPIO (ESP32-C3 Super Mini)**:
  - GPIO8: LED integrado (verde)
  - GPIO7: LED externo (configurable)
  - BUTTON_GPIO: Botón externo (opcional, actualmente None)

## Arranque rápido

### 1. Preparar entorno
```bash
cd ~/proyectos/iot/museiq/iot-museiq
source .venv/bin/activate
```

### 2. Ubicar puerto serial
```bash
ls -l /dev/ttyACM*
```
Típicamente: `/dev/ttyACM0` (puede variar si hay múltiples puertos)

### 3. Verificar conexión
```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 repl
```
Presiona `Ctrl+]` o `Ctrl+x` para salir del REPL.

## Cargar Firmware

### Beacon (`museiq.py`)
```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 fs cp museiq.py :main.py
.venv/bin/python -m mpremote connect /dev/ttyACM0 reset
```

### Servicio Bidireccional Genérico
```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 fs cp testApp/bidir.py :main.py
.venv/bin/python -m mpremote connect /dev/ttyACM0 reset
```

### Variantes Preconfigradas
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

### Tests de LEDs
**Ambos LEDs alternando (dual blink):**
```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 fs cp dual_led_test.py :main.py
.venv/bin/python -m mpremote connect /dev/ttyACM0 reset
```

**Solo GPIO7 (LED externo):**
```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 fs cp led7_test.py :main.py
.venv/bin/python -m mpremote connect /dev/ttyACM0 reset
```

**Solo GPIO8 (LED integrado):**
```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 fs cp led8_test.py :main.py
.venv/bin/python -m mpremote connect /dev/ttyACM0 reset
```

## Control Directo de GPIO desde Terminal

**Encender LED integrado (GPIO8):**
```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 exec "from machine import Pin; Pin(8, Pin.OUT).value(1)"
```

**Apagar LED integrado (GPIO8):**
```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 exec "from machine import Pin; Pin(8, Pin.OUT).value(0)"
```

**Encender LED externo (GPIO7):**
```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 exec "from machine import Pin; Pin(7, Pin.OUT).value(1)"
```

**Apagar LED externo (GPIO7):**
```bash
.venv/bin/python -m mpremote connect /dev/ttyACM0 exec "from machine import Pin; Pin(7, Pin.OUT).value(0)"
```

## Formatos de Datos y Protocolos

### Beacon BLE (museiq.py)

#### Service Data (UUID 0xA00A)
Estructura de **12 bytes** enviada en cada advertising:

| Campo | Bytes | Tipo | Rango | Ejemplo |
|-------|-------|------|-------|---------|
| ROOM_ID | 6 | UTF-8 String | N/A | `"SALA_1"` |
| BEACON_NODE | 1 | UInt8 | 1-255 | `0x02` (2) |
| FW_VERSION_MAJOR | 1 | UInt8 | 0-255 | `0x01` |
| FW_VERSION_MINOR | 1 | UInt8 | 0-255 | `0x00` |
| TX_POWER_DBM | 1 | Int8 (signed) | -128 a 127 | `-12` dBm |
| BATTERY_MV | 2 | UInt16 LE | 0-65535 | `0xE70E` (3700 mV) |

**Empaquetamiento struct**: `"6sBBBbH"` (little-endian)

**Ejemplo codificado (hex**):
```
Service Data (0xA00A):
53 41 4C 41 5F 31 | 02 | 01 | 00 | F4 | 0E E7
SALA_1            | B2 | v1 | v0 | -12| 3700mV
```

#### GATTS Characteristics
- **0xA00B (READ)**: Beacon ID formateado como `"{ROOM_ID}-B{BEACON_NODE:02d}"`
  - Ejemplo: `"SALA_1-B02"` (9 bytes UTF-8)
- **0xA00C (READ)**: TX Power como entero signed (1 byte)
  - Ejemplo: `-12` (0xF4 en two's complement)

### Servicio Bidireccional (testApp/bidir.py)

#### UUIDs Service
- **Service UUID**: `0xA100`
- **RX Characteristic (0xA101)**: App escribe, ESP32 lee
  - Flags: `WRITE | WRITE_NO_RESPONSE`
  - Max 20 bytes por write (BLE MTU estándar)
- **TX Characteristic (0xA102)**: ESP32 escribe, app lee
  - Flags: `READ | NOTIFY`
  - Max 20 bytes por notificación

#### Comandos (RX - App → ESP32)
Enviados como **UTF-8 strings** (case-insensitive después de `.upper()`):

| Comando | Descripción | Respuesta Esperada |
|---------|--------------|-------------------|
| `LED1_ON` | Enciende LED1 (GPIO8) | `"LED1_GPIO8_ON"` |
| `LED1_OFF` | Apaga LED1 (GPIO8) | `"LED1_GPIO8_OFF"` |
| `LED2_ON` | Enciende LED2 (GPIO7) | `"LED2_GPIO7_ON"` |
| `LED2_OFF` | Apaga LED2 (GPIO7) | `"LED2_GPIO7_OFF"` |
| `LED_PIN36_ON` | Legacy (mapea a LED1) | `"LED1_GPIO8_ON"` |
| `LED_PIN36_OFF` | Legacy (mapea a LED1) | `"LED1_GPIO8_OFF"` |
| *(texto libre)* | No es comando | `"Recibido: {texto}"` |

**Ejemplo intercambio (hex)**:
```
App → ESP32: 4C 45 44 31 5F 4F 4E        (UTF-8: "LED1_ON")
ESP32 → App: 4C 45 44 31 5F 47 50 49 4F 38 5F 4F 4E  (UTF-8: "LED1_GPIO8_ON")
```

#### Respuestas (TX - ESP32 → App)
Formato: **UTF-8 strings**, max ~20 bytes

| Respuesta | Descripción |
|-----------|-------------|
| `"LED{N}_GPIO{pin}_{ON\|OFF}"` | Confirmación de comando exitoso |
| `"ERROR_LED{N}: GPIO{pin} no disponible"` | GPIO no configurado/disponible |
| `"Recibido: {texto}"` | Echo de mensaje no comando |
| `"Hola desde ESP32"` | Mensaje inicial al conectar |

**Nota**: El encoding es UTF-8. Si el cliente no puede decodificar, aparece como `(hex)` en los logs.

#### Device Names
Configurable, típicamente:
- `"ESP32-C3-Bidir"` (genérico)
- `"S1-M1"`, `"S1-M2"`, `"S1-M3"` (preconfigrados)
- Formato libre, max 20 caracteres recomendados

### Advertising Payload (ambos servicios)
Estructura BLE estándar en advertising:

```
AD Type 0x01 (Flags):           0x06 (LE General Discoverable)
AD Type 0x09 (Local Name):      Device name (UTF-8, variable)
AD Type 0x16 (Service Data):    [UUID_16 (LE)] + custom data
AD Type 0x0A (TX Power):        TX Power calibrado (Int8)
```

Intervalo: **500 ms** (configurable en `ADV_INTERVAL_US`)

### Configuraciones Típicas

#### Museo/Sala (Beacon)
```python
ROOM_ID = "SALA_1"
BEACON_NODE = 2
FW_VERSION = (1, 0)
TX_POWER_DBM = -12      # Distancias cortas (~2-3m)
# o -4 dBm para distancias largas (4-10m)
```

#### Control Local (Bidireccional)
```python
ROOM_CODE = "S1"
MINI_CODE = "M1"
DEVICE_NAME = "S1-M1"
LED1_GPIO = 8
LED2_GPIO = 7
BUTTON_GPIO = None      # Habilitar si se conecta botón externo
```

## Troubleshooting

### Beacon no visible en scanning
- Verifica `LOG_VERBOSE = True` en código para ver advertising status
- Comprueba que el ESP32 tiene firmware MicroPython válido
- Ajusta `TX_POWER_DBM` (valores más altos = alcance mayor)

### LEDs no responden a comandos
- Verifica GPIO en `LED1_GPIO` y `LED2_GPIO`
- Confirma que los LEDs están conectados correctamente (anodo a GPIO, cátodo a GND con resistencia)
- Prueba directo con comandos de terminal (ver sección "Control Directo")

### Errores en REPL
- Usa `disconnect` y `reset` para limpiar estado
- Si `PORT not found`, verifica `/dev/ttyACM*`
- Si MicroPython no carga, reflashea el ESP32

## Referencias

- **MicroPython BLE**: https://docs.micropython.org/en/latest/library/ubluetooth.html
- **ESP32-C3 Pinout**: Datasheet oficial Espressif
- **BLE Advertising**: Bluetooth Core Spec Vol 3, Part C, Section 11

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
