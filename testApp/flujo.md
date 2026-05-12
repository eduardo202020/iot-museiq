### Flujo de trabajo para testApp (BLE bidireccional)

> **Linux** — puerto: `/dev/ttyUSB0` (ajusta si difiere). Ejecuta desde la raíz del proyecto.

**Activar entorno virtual:**
```bash
cd ~/proyectos/iot/iot-museiq
source .venv/bin/activate
```

**Editar código:**
- Edita `testApp/bidir.py` en VSCode

**Perfiles por mini:**
- `testApp/mini_1.py` -> BLE name `S1-M1`, identificador TX inicial `S1|M1|TX=-12`
- `testApp/mini_2.py` -> BLE name `S1-M2`, identificador TX inicial `S1|M2|TX=-12`
- `testApp/mini_3.py` -> BLE name `S1-M3`, identificador TX inicial `S1|M3|TX=-12`

**Subir y ejecutar en ESP32:**
```bash
.venv/bin/python -m mpremote connect /dev/ttyUSB0 fs cp testApp/bidir.py :main.py
.venv/bin/python -m mpremote connect /dev/ttyUSB0 reset
```

**Ejemplo para un mini identificado:**
```bash
.venv/bin/python -m mpremote connect /dev/ttyUSB0 fs cp testApp/mini_2.py :main.py
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
- Escanea y conecta al dispositivo `ESP32-C3-Bidir` o a `S1-M1` / `S1-M2` / `S1-M3` si cargaste uno de los perfiles dedicados.
- Característica RX (`0xA101`): escribe un texto o número.
- Característica TX (`0xA102`): lee la respuesta (eco) o recibe notificación.
- Verás logs en el REPL cada vez que la app escriba.

**Comandos para controlar LED desde la app (RX 0xA101):**
- `LED1_ON`  (GPIO8 por defecto en `ESP32-C3 Super Mini`)
- `LED1_OFF` (GPIO8 por defecto)
- `LED2_ON`  (GPIO7 por defecto)
- `LED2_OFF` (GPIO7 por defecto)

**Respuesta esperada por TX (0xA102):**
- `LED1_GPIO8_ON/OFF` si mantienes la configuracion por defecto
- `LED2_GPIO7_ON/OFF` si mantienes la configuracion por defecto

**Envio de señal por boton fisico:**
- Por defecto el boton esta deshabilitado (`BUTTON_GPIO = None`).
- Si conectas uno externo, asigna `BUTTON_GPIO` a un pin seguro y conectalo a GND usando `PULL_UP` interno.
- Al presionar, el ESP32 envia por TX: `BOTON_GPIOx_PRESS`.
- Al soltar, el ESP32 envia por TX: `BOTON_GPIOx_RELEASE`.
- En la app debes habilitar notificaciones/monitor en TX (`0xA102`) para recibir estos eventos en tiempo real.

**Diagnóstico rápido si no conecta:**
- Debes ver en REPL: `Iniciando BLE bidireccional...` y `Advertising (bidireccional...)`.
- Si no aparecen, vuelve a copiar `testApp\\bidir.py` a `:main.py` y resetea el ESP32.
- Verifica permisos Bluetooth/ubicación en el teléfono y que no esté conectado a otro central.

¿Quieres ejemplos de código para la app Expo/React Native? Pídelo y te los preparo.
