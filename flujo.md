### **2. Flujo de trabajo diario**

**Activar entorno virtual:**
```powershell
cd C:\Users\pc\Documents\iot
.venv\Scripts\Activate.ps1
```

**Editar código:**
- Edita museiq.py en VSCode

**Subir y ejecutar:**
```powershell
.\.venv\Scripts\python.exe -m mpremote connect COM5 fs cp museiq.py :main.py
.\.venv\Scripts\python.exe -m mpremote connect COM5 reset
```

**Ver salida en tiempo real (REPL):**
```powershell
.\.venv\Scripts\python.exe -m mpremote connect COM5 repl
```
_(Salir con `Ctrl+]` o `Ctrl+x`)_

**Ejecutar sin guardar (prueba rápida):**
```powershell
.\.venv\Scripts\python.exe -m mpremote connect COM5 run museiq.py
```

---

### Simular ubicación BLE sin ESP32

Desde Linux/WSL:

```bash
cd /home/eduardo/proyectos/iot/museiq/iot-museiq
python dev_location_bridge.py --host 0.0.0.0 --port 8787
```

Comandos dentro del simulador:

- `1` a `6`: simula Sala 1, zona/obra exacta.
- `vr` o `s4`: simula Sala VR y activa modo inmersivo.
- `clear`: pausa la ubicación simulada.
- `status`: imprime el JSON que consume la app.
- `q`: salir.

En `museiqApp`, iniciar Metro normalmente:

```bash
cd /home/eduardo/proyectos/iot/museiq/museiqApp
npx expo start --dev-client --host lan -c
```

Si la app no descubre el bridge automáticamente:

```bash
EXPO_PUBLIC_MUSEIQ_BLE_SIM_URL=http://<IP_PC>:8787 npx expo start --dev-client --host lan -c
```
