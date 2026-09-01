# Harness de iot-museiq

Este nodo publica la capacidad `museiq.location.v1` y conoce los manifiestos
de `museiqApp` y `museRAG`. El bridge HTTP es la implementacion de escritorio
del contrato; el firmware BLE sigue siendo la fuente fisica real.

## Diagnostico

Desde la raiz de `iot-museiq`:

```bash
# Solo manifiesto, referencias y conocimiento de pares.
python3 harness/doctor.py --offline

# Salud de iot-museiq y MuseRAG.
python3 harness/doctor.py

# Solo este proveedor.
python3 harness/doctor.py --service iot-museiq
```

Las URLs se resuelven desde `MUSEIQ_IOT_URL` y `MUSEIQ_RAG_URL`; tambien se
pueden pasar con `--iot-url` y `--rag-url`.

## Comunicacion

```text
ESP32 BLE -> museiqApp
bridge /state -> museiqApp (solo modo harness)
museiqApp -> MuseRAG /api/preguntar
```

`iot-museiq` no llama directamente a MuseRAG: conoce ese nodo para diagnostico
y trazabilidad, mientras `museiqApp` media el contexto fisico hacia la consulta
curatorial. La definicion versionada esta en [manifest.json](manifest.json).
