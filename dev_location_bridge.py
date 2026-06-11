#!/usr/bin/env python3
"""Dev bridge para simular ubicacion BLE de MuseIQ desde la terminal.

Uso:
  python dev_location_bridge.py --host 0.0.0.0 --port 8787

La app museiqApp consulta GET /state y recibe un beacon dominante simulado.
Esto permite validar el flujo Sala 1 -> Sala VR sin ESP32 fisicos.
"""

from __future__ import annotations

import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse


SALA_1_ZONES = [
    {
        "artworkId": "obra-1-1-L",
        "beaconNode": 1,
        "label": "Zona 1 - Obra 1",
        "qrCodes": ["SALA_1-01-A", "SALA_1-01-B"],
    },
    {
        "artworkId": "obra-1-1-C",
        "beaconNode": 2,
        "label": "Zona 2 - Obra 2",
        "qrCodes": ["SALA_1-02-A", "SALA_1-02-B"],
    },
    {
        "artworkId": "obra-1-1-R",
        "beaconNode": 3,
        "label": "Zona 3 - Obra 3",
        "qrCodes": ["SALA_1-03-A", "SALA_1-03-B"],
    },
    {
        "artworkId": "obra-1-2-L",
        "beaconNode": 4,
        "label": "Zona 4 - Obra 4",
        "qrCodes": ["SALA_1-04-A", "SALA_1-04-B"],
    },
    {
        "artworkId": "obra-1-2-C",
        "beaconNode": 5,
        "label": "Zona 5 - Obra 5",
        "qrCodes": ["SALA_1-05-A", "SALA_1-05-B"],
    },
    {
        "artworkId": "obra-1-2-R",
        "beaconNode": 6,
        "label": "Zona 6 - Obra 6",
        "qrCodes": ["SALA_1-06-A", "SALA_1-06-B"],
    },
]


class LocationState:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._state: dict[str, Any] = {
            "beacon": None,
            "enabled": False,
            "message": "Simulador listo. Selecciona una zona.",
            "updatedAt": int(time.time() * 1000),
        }

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return dict(self._state)

    def clear(self) -> dict[str, Any]:
        with self._lock:
            self._state = {
                "beacon": None,
                "enabled": False,
                "message": "Ubicacion simulada pausada.",
                "updatedAt": int(time.time() * 1000),
            }
            return dict(self._state)

    def set_sala_1_zone(self, zone_number: int, rssi: int = -42) -> dict[str, Any]:
        if zone_number < 1 or zone_number > len(SALA_1_ZONES):
            raise ValueError("La zona de SALA_1 debe estar entre 1 y 6.")

        zone = SALA_1_ZONES[zone_number - 1]
        now = int(time.time() * 1000)
        beacon = {
            "artworkId": zone["artworkId"],
            "battery": 3700,
            "beaconNode": zone["beaconNode"],
            "deviceAddress": f"SIM:SALA_1:{zone_number}",
            "firmwareMajor": 1,
            "firmwareMinor": 0,
            "firmwareVersion": "sim",
            "id": f"SALA_1-SIM-Z{zone_number:02d}",
            "qrCodes": zone["qrCodes"],
            "roomId": "SALA_1",
            "rssi": rssi,
            "txPower": -8,
            "txPowerPayload": -8,
            "zoneId": f"Z{zone_number}",
            "zoneLabel": zone["label"],
        }

        with self._lock:
            self._state = {
                "beacon": beacon,
                "enabled": True,
                "message": f"SALA_1 -> {zone['label']} ({zone['artworkId']})",
                "updatedAt": now,
            }
            return dict(self._state)

    def set_sala_vr(self, rssi: int = -40) -> dict[str, Any]:
        now = int(time.time() * 1000)
        beacon = {
            "battery": 3700,
            "beaconNode": 4,
            "deviceAddress": "SIM:SALA_VR:S4",
            "firmwareMajor": 1,
            "firmwareMinor": 0,
            "firmwareVersion": "sim",
            "id": "SALA_VR-SIM-S4",
            "roomId": "SALA_VR",
            "rssi": rssi,
            "txPower": -8,
            "txPowerPayload": -8,
            "zoneId": "S4",
            "zoneLabel": "Sala VR - modo inmersivo",
        }

        with self._lock:
            self._state = {
                "beacon": beacon,
                "enabled": True,
                "message": "SALA_VR -> modo inmersivo disponible",
                "updatedAt": now,
            }
            return dict(self._state)


def make_handler(location_state: LocationState) -> type[BaseHTTPRequestHandler]:
    class DevLocationHandler(BaseHTTPRequestHandler):
        def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self) -> None:  # noqa: N802
            self._send_json({"ok": True})

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)

            if parsed.path == "/health":
                self._send_json({"ok": True, "service": "museiq-dev-location-bridge"})
                return

            if parsed.path == "/state":
                self._send_json(location_state.snapshot())
                return

            if parsed.path == "/set":
                self._handle_set(parse_qs(parsed.query))
                return

            self._send_json({"error": "Ruta no encontrada"}, status=404)

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path != "/set":
                self._send_json({"error": "Ruta no encontrada"}, status=404)
                return

            length = int(self.headers.get("Content-Length", "0") or "0")
            raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            try:
                body = json.loads(raw_body)
            except json.JSONDecodeError:
                self._send_json({"error": "JSON invalido"}, status=400)
                return

            self._handle_set({key: [str(value)] for key, value in body.items()})

        def _handle_set(self, params: dict[str, list[str]]) -> None:
            try:
                room = (params.get("room") or params.get("sala") or [""])[0].strip().lower()
                zone = (params.get("zone") or params.get("zona") or [""])[0].strip().lower()

                if room in {"vr", "sala_vr", "salavr"} or zone in {"vr", "s4"}:
                    self._send_json(location_state.set_sala_vr())
                    return

                if zone in {"clear", "none", "pausa"}:
                    self._send_json(location_state.clear())
                    return

                zone_number = int(zone or (params.get("beaconNode") or [""])[0])
                self._send_json(location_state.set_sala_1_zone(zone_number))
            except Exception as exc:  # noqa: BLE001
                self._send_json({"error": str(exc), "state": location_state.snapshot()}, status=400)

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            return

    return DevLocationHandler


def print_menu(host: str, port: int) -> None:
    print("\nMuseIQ Dev Location Bridge")
    print("==========================")
    print(f"HTTP: http://{host}:{port}")
    print("Config app: EXPO_PUBLIC_MUSEIQ_BLE_SIM_URL=http://<IP_PC>:%s" % port)
    print("\nComandos:")
    print("  1..6      -> SALA_1, zona/obra exacta")
    print("  vr | s4   -> SALA_VR, modo inmersivo")
    print("  clear     -> pausar ubicacion simulada")
    print("  status    -> ver estado actual")
    print("  help      -> mostrar comandos")
    print("  q         -> salir")


def run_terminal(location_state: LocationState, server: ThreadingHTTPServer, host: str, port: int) -> None:
    print_menu(host, port)

    while True:
        try:
            command = input("\nMuseIQ sim> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            command = "q"

        if command in {"q", "quit", "exit"}:
            print("Cerrando simulador...")
            server.shutdown()
            return

        if command in {"help", "h", "?"}:
            print_menu(host, port)
            continue

        if command in {"status", "s"}:
            print(json.dumps(location_state.snapshot(), indent=2, ensure_ascii=False))
            continue

        if command in {"clear", "none", "pausa"}:
            state = location_state.clear()
            print(state["message"])
            continue

        if command in {"vr", "s4", "sala_vr", "salavr"}:
            state = location_state.set_sala_vr()
            print(state["message"])
            continue

        try:
            zone_number = int(command)
            state = location_state.set_sala_1_zone(zone_number)
            print(state["message"])
        except Exception as exc:  # noqa: BLE001
            print(f"Comando no reconocido: {command!r}. Error: {exc}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simula beacons BLE para MuseIQ.")
    parser.add_argument("--host", default="0.0.0.0", help="Host HTTP del bridge.")
    parser.add_argument("--port", default=8787, type=int, help="Puerto HTTP del bridge.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    location_state = LocationState()
    server = ThreadingHTTPServer((args.host, args.port), make_handler(location_state))
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    try:
        run_terminal(location_state, server, args.host, args.port)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
