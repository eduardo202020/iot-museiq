### Flujo de trabajo para testApp (BLE bidireccional)

> **Linux** — puerto: `/dev/ttyUSB0` (ajusta si difiere). Ejecuta desde la raíz del proyecto.

**Activar entorno virtual:**
```bash
cd ~/proyectos/iot/iot-museiq
source .venv/bin/activate
```

**Editar código:**
- Edita `testApp/bidir.py` en VSCode

**Subir y ejecutar en ESP32:**
```bash
.venv/bin/python -m mpremote connect /dev/ttyUSB0 fs cp testApp/bidir.py :main.py
.venv/bin/python -m mpremote connect /dev/ttyUSB0 reset
```

**Ver salida en tiempo real (REPL):**
```bash
.venv/bin/python -m mpremote connect /dev/ttyUSB0 repl
```
_(Salir con `Ctrl+]` o `Ctrl+x`)_

**Prueba en REPL (envio ESP32 -> app):**
```python
import main
main.send_text('Hola app, desde REPL')
```

**Ejecutar sin guardar (prueba rápida):**
```bash
.venv/bin/python -m mpremote connect /dev/ttyUSB0 run testApp/bidir.py
```

---

**Prueba desde la app:**
- Escanea y conecta al dispositivo `ESP32-Bidir`.
- Característica RX (`0xA101`): escribe un texto o número.
- Característica TX (`0xA102`): lee la respuesta (eco) o recibe notificación.
- Verás logs en el REPL cada vez que la app escriba.

**Comandos para controlar LED desde la app (RX 0xA101):**
- `LED1_ON`  (GPIO2)
- `LED1_OFF` (GPIO2)
- `LED2_ON`  (GPIO15)
- `LED2_OFF` (GPIO15)

**Respuesta esperada por TX (0xA102):**
- `LED1_GPIO2_ON/OFF`
- `LED2_GPIO15_ON/OFF`

**Envio de señal por boton fisico:**
- Conecta un boton a `GPIO0` (a GND, usando `PULL_UP` interno).
- Al presionar, el ESP32 envia por TX: `BTN_GPIO0_PRESS`.
- Al soltar, el ESP32 envia por TX: `BTN_GPIO0_RELEASE`.
- En la app debes habilitar notificaciones/monitor en TX (`0xA102`) para recibir estos eventos en tiempo real.

**Diagnóstico rápido si no conecta:**
- Debes ver en REPL: `Iniciando BLE bidireccional...` y `Advertising (bidireccional...)`.
- Si no aparecen, vuelve a copiar `testApp\\bidir.py` a `:main.py` y resetea el ESP32.
- Verifica permisos Bluetooth/ubicación en el teléfono y que no esté conectado a otro central.

¿Quieres ejemplos de código para la app Expo/React Native? Pídelo y te los preparo.
