# Guia para agentes

## Alcance

Este archivo aplica a todo `iot-museiq`. El repositorio contiene firmware
MicroPython para ESP32/ESP32-C3 y un simulador HTTP de ubicacion para
`museiqApp`. No mezcles ambos runtimes: el firmware corre en MicroPython y
`dev_location_bridge.py` corre en Python de escritorio.

## Rol dentro del ecosistema

`iot-museiq` produce el contexto fisico del recorrido:

```text
ESP32 BLE o simulador HTTP
-> sala + nodo/zona + RSSI
-> museiqApp
-> sugerencia de obra o entrada a SALA_VR
```

La marca externa puede presentarse como ArkeIA, pero conserva identificadores
tecnicos como `MuseIQ`, `SALA_1`, `SALA_VR` y los UUID BLE mientras no exista
una migracion coordinada con la app.

## Fuente de verdad

- `museiq.py`: beacon BLE principal.
- `testApp/bidir.py`: servicio BLE bidireccional generico.
- `testApp/mini_*.py`: perfiles de hardware preconfigurados.
- `dev_location_bridge.py`: simulador que consume la app movil.
- `harness/manifest.json`: identidad, capacidades y pares del nodo IoT.
- `harness/doctor.py`: diagnostico local y conectividad entre nodos.
- `README.md`: protocolo, cableado y operacion.
- `flujo.md` y `testApp/flujo.md`: comandos rapidos de laboratorio.

## Contratos que no deben romperse

- Service Data UUID: `0xA00A`.
- Caracteristicas de lectura: `0xA00B` y `0xA00C`.
- Payload de advertising: `struct "6sBBBbH"`, 12 bytes y little-endian.
- `ROOM_ID` ocupa 6 bytes; los valores activos son `SALA_1` y `SALA_VR`.
- El bridge escucha por defecto en `0.0.0.0:8787`.
- `GET /health`, `GET /state` y `GET|POST /set` son consumidos por
  `museiqApp`.
- Las zonas `1..6` deben conservar `artworkId`, `beaconNode` y dos QR
  consistentes con el catalogo de la app.
- `vr`/`s4` debe emitir `roomId: "SALA_VR"` y no sugerir una obra normal.

Si cambias cualquiera de estos contratos, actualiza en el mismo trabajo
`museiqApp/hooks/use-ble-scanner.ts`,
`museiqApp/hooks/use-simulated-ble-location.ts`, tipos relacionados y
documentacion.

## Harness distribuido

Este repositorio es el nodo `iot-museiq` de una topologia de tres proyectos.
Conoce explicitamente a `museiqApp` y `museRAG` mediante
`harness/manifest.json`. Antes de cambiar una frontera entre repositorios:

```bash
python3 harness/doctor.py --offline
cd ../museiq-harness && python3 -m museiq_harness topology
```

No agregues una llamada directa de firmware o bridge hacia MuseRAG: la ruta
normal es `iot-museiq -> museiqApp -> museRAG`. El conocimiento del tercer nodo
sirve para validar topologia, contratos y diagnostico del sistema completo.

## Estilo de implementacion

- Usa ASCII salvo que el archivo ya necesite texto en espanol.
- Mantener el firmware compatible con MicroPython: evita dependencias de
  CPython, `dataclasses`, APIs de `pathlib` y sintaxis no soportada por la
  version instalada en el ESP32.
- Mantener `dev_location_bridge.py` tipado y compatible con Python 3.11+.
- Centraliza valores de sala, nodo, potencia y GPIO en constantes al inicio de
  cada firmware.
- No ocultes errores de protocolo; los fallos del bridge deben devolver JSON
  con estado HTTP apropiado.
- Los logs de firmware deben ser breves. Usa `LOG_VERBOSE` para diagnostico y
  evita imprimir en cada advertising en produccion.

## Entorno y comandos

Preparar entorno:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Ejecutar el simulador:

```bash
python dev_location_bridge.py --host 0.0.0.0 --port 8787
```

Comprobar el bridge:

```bash
curl http://127.0.0.1:8787/health
curl http://127.0.0.1:8787/state
curl "http://127.0.0.1:8787/set?zone=1"
curl "http://127.0.0.1:8787/set?zone=vr"
```

Comprobar puertos y dispositivo:

```bash
.venv/bin/python -m mpremote connect list
.venv/bin/python -m mpremote connect /dev/ttyACM0 repl
```

No asumas que el puerto es `/dev/ttyACM0`; descubre el puerto antes de cargar
firmware.

## Validacion minima

Para cambios de Python de escritorio:

```bash
python -m py_compile dev_location_bridge.py
```

Para cambios del contrato simulado, valida al menos:

1. zona `1`;
2. zona `6`;
3. `vr`;
4. `clear`;
5. consumo desde un celular con `EXPO_PUBLIC_MUSEIQ_BLE_SIM_URL`.

Para firmware, la validacion real requiere ESP32: copiar como `main.py`,
reiniciar y observar el REPL. No flashees ni sobrescribas un dispositivo
conectado salvo que la tarea lo solicite.

## Archivos y Git

- No versionar `.venv/`, `__pycache__/` ni configuracion local del editor.
- Trata los binarios en `firmware/` como artefactos deliberados; no reemplaces
  ni agregues firmware pesado sin indicarlo.
- No borres perfiles `mini_*` ni scripts de GPIO aunque parezcan duplicados:
  representan configuraciones fisicas distintas.
- Usa commits breves y enfocados, por ejemplo `feat: add room beacon profile` o
  `fix: keep vr simulator room context`.
