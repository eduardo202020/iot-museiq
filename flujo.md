### **2. Flujo de trabajo diario**

**Activar entorno virtual:**
```powershell
cd C:\Users\pc\Documents\iot
.venv\Scripts\Activate.ps1
```

**Editar código:**
- Edita main.py en VSCode

**Subir y ejecutar:**
```powershell
python -m mpremote connect COM5 fs cp main.py :main.py + reset
```

**Ver salida en tiempo real (REPL):**
```powershell
python -m mpremote connect COM5 repl
```
_(Salir con `Ctrl+]` o `Ctrl+x`)_

**Ejecutar sin guardar (prueba rápida):**
```powershell
python -m mpremote connect COM5 run main.py
```

---

