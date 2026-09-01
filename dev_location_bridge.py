#!/usr/bin/env python3
"""Dev bridge para simular ubicacion BLE de MuseIQ desde la terminal.

Uso:
  python dev_location_bridge.py --host 0.0.0.0 --port 8787

La app museiqApp consulta GET /state y recibe un beacon dominante simulado.
Esto permite validar las tres salas tematicas y Sala VR sin ESP32 fisicos.
"""

from __future__ import annotations

import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse


ROOM_CATALOG = {
    "SALA_1": {
        "beaconNode": 1,
        "label": "Conocimiento de la UNI",
        "artworks": [
            ("obra-1-1-L", "Escritorio historico y legado de Habich"),
            ("obra-1-1-C", "Maquina de escribir"),
            ("obra-1-1-R", "Busto de Miguel Grau"),
            ("obra-1-2-L", "Busto de Jose de San Martin"),
        ],
    },
    "SALA_2": {
        "beaconNode": 2,
        "label": "Minerales del Peru",
        "artworks": [
            ("mineral-bornita", "Bornita"),
            ("mineral-esfalerita", "Esfalerita"),
            ("mineral-magnetita", "Magnetita"),
            ("mineral-wolframita", "Wolframita"),
            ("mineral-azurita", "Azurita"),
            ("obra-1-2-C", "Malaquita y cobre"),
            ("mineral-galena", "Galena"),
            ("mineral-oro", "Muestra rotulada como oro"),
            ("mineral-pirita", "Pirita"),
            ("mineral-plata", "Muestra rotulada como plata"),
        ],
    },
    "SALA_3": {
        "beaconNode": 3,
        "label": "Culturas antiguas del Peru",
        "artworks": [
            ("cultura-musico-moche", "Musico moche"),
            ("cultura-botella-chimu", "Botella Chimu-Lambayeque"),
            ("obra-1-2-R", "Aribalo inca de referencia"),
            ("cultura-asiento-inca", "Asiento del Inca de referencia"),
            ("cultura-botella-chavin", "Botella Chavin 204002"),
            ("cultura-obelisco-tello", "Obelisco Tello de referencia"),
        ],
    },
}

ROOM_PREFIXES = {"u": "SALA_1", "m": "SALA_2", "c": "SALA_3"}
ROOM_ALIASES = {
    "1": "SALA_1", "s1": "SALA_1", "sala1": "SALA_1", "sala_1": "SALA_1", "uni": "SALA_1",
    "2": "SALA_2", "s2": "SALA_2", "sala2": "SALA_2", "sala_2": "SALA_2", "minerales": "SALA_2",
    "3": "SALA_3", "s3": "SALA_3", "sala3": "SALA_3", "sala_3": "SALA_3", "culturas": "SALA_3",
}

VR_COMMANDS = {
    "s4",
    "sala vr",
    "sala_vr",
    "salavr",
    "vr",
    "vr | s4",
    "vr/s4",
    "vr|s4",
}


def resolve_room_artwork(room: str, zone: str) -> tuple[str, int]:
    """Resolve room/order while preserving plain 1..4 as legacy SALA_1 zones."""
    normalized_room = ROOM_ALIASES.get(room, room.upper()) if room else ""
    if normalized_room in ROOM_CATALOG:
        return normalized_room, int(zone or "1")

    if len(zone) >= 2 and zone[0] in ROOM_PREFIXES and zone[1:].isdigit():
        return ROOM_PREFIXES[zone[0]], int(zone[1:])

    if zone in {"s1", "s2", "s3"}:
        return ROOM_ALIASES[zone], 1

    return "SALA_1", int(zone)


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

    def set_room_artwork(
        self,
        room_id: str,
        artwork_order: int,
        rssi: int = -42,
    ) -> dict[str, Any]:
        room = ROOM_CATALOG.get(room_id)
        if room is None:
            raise ValueError("La sala debe ser SALA_1, SALA_2 o SALA_3.")

        artworks = room["artworks"]
        if artwork_order < 1 or artwork_order > len(artworks):
            raise ValueError(
                f"La obra de {room_id} debe estar entre 1 y {len(artworks)}."
            )

        artwork_id, artwork_label = artworks[artwork_order - 1]
        now = int(time.time() * 1000)
        qr_base = f"{room_id}-{artwork_order:02d}"
        beacon = {
            "artworkId": artwork_id,
            "battery": 3700,
            "beaconNode": room["beaconNode"],
            "deviceAddress": f"SIM:{room_id}:{artwork_order}",
            "firmwareMajor": 1,
            "firmwareMinor": 0,
            "firmwareVersion": "sim",
            "id": f"{room_id}-SIM-Z{artwork_order:02d}",
            "qrCodes": [f"{qr_base}-A", f"{qr_base}-B"],
            "roomId": room_id,
            "rssi": rssi,
            "txPower": -8,
            "txPowerPayload": -8,
            "zoneId": f"{room_id}-Z{artwork_order}",
            "zoneLabel": f"{room['label']} - {artwork_label}",
        }

        with self._lock:
            self._state = {
                "beacon": beacon,
                "enabled": True,
                "message": f"{room_id} -> {artwork_label} ({artwork_id})",
                "updatedAt": now,
            }
            return dict(self._state)

    def set_sala_1_zone(self, zone_number: int, rssi: int = -42) -> dict[str, Any]:
        """Compatibilidad con clientes anteriores que simulaban solo SALA_1."""
        return self.set_room_artwork("SALA_1", zone_number, rssi)

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

                if room in VR_COMMANDS or zone in VR_COMMANDS:
                    self._send_json(location_state.set_sala_vr())
                    return

                if zone in {"clear", "none", "pausa"}:
                    self._send_json(location_state.clear())
                    return

                zone = zone or (params.get("beaconNode") or [""])[0].strip().lower()
                room_id, artwork_order = resolve_room_artwork(room, zone)
                self._send_json(location_state.set_room_artwork(room_id, artwork_order))
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
    print("  u1..u4    -> Conocimiento de la UNI")
    print("  m1..m10   -> Minerales del Peru")
    print("  c1..c6    -> Culturas antiguas del Peru")
    print("  s1|s2|s3 -> primera pieza de cada sala")
    print("  1..4      -> alias compatible de u1..u4")
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

        if command in VR_COMMANDS:
            state = location_state.set_sala_vr()
            print(state["message"])
            continue

        try:
            room_id, artwork_order = resolve_room_artwork("", command)
            state = location_state.set_room_artwork(room_id, artwork_order)
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
