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

