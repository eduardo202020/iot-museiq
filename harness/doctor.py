from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


MANIFEST_PATH = Path(__file__).with_name("manifest.json")
EXPECTED_NODE_ID = "iot-museiq"


class DoctorError(RuntimeError):
    """A distributed harness check failed."""


def _load_json_file(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DoctorError(f"No se pudo leer {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise DoctorError(f"{path} debe contener un objeto JSON.")
    return payload


def _check_manifests() -> dict[str, Any]:
    manifest = _load_json_file(MANIFEST_PATH)
    if manifest.get("schemaVersion") != 1:
        raise DoctorError("schemaVersion debe ser 1.")
    if manifest.get("id") != EXPECTED_NODE_ID:
        raise DoctorError(
            f"Se esperaba el nodo {EXPECTED_NODE_ID!r}, no {manifest.get('id')!r}."
        )

    peers = manifest.get("peers")
    if not isinstance(peers, list) or len(peers) != 2:
        raise DoctorError("El nodo debe declarar exactamente sus otros dos pares.")

    peer_ids: list[str] = []
    for peer in peers:
        if not isinstance(peer, dict):
            raise DoctorError("Cada peer debe ser un objeto.")
        peer_id = peer.get("id")
        relative_manifest = peer.get("manifest")
        if not isinstance(peer_id, str) or not isinstance(relative_manifest, str):
            raise DoctorError("Cada peer necesita id y manifest.")
        peer_path = (MANIFEST_PATH.parent / relative_manifest).resolve()
        peer_manifest = _load_json_file(peer_path)
        if peer_manifest.get("id") != peer_id:
            raise DoctorError(
                f"{peer_path} declara {peer_manifest.get('id')!r}, no {peer_id!r}."
            )
        peer_ids.append(peer_id)

    return {"node": EXPECTED_NODE_ID, "peers": sorted(peer_ids)}


def _get_json(url: str, timeout: float) -> dict[str, Any]:
    request = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, OSError, json.JSONDecodeError) as exc:
        raise DoctorError(f"GET {url}: {exc}") from exc
    if not isinstance(payload, dict):
        raise DoctorError(f"GET {url}: la respuesta no es un objeto JSON.")
    return payload


def _validate_iot_health(payload: dict[str, Any]) -> None:
    if payload.get("ok") is not True or not isinstance(payload.get("service"), str):
        raise DoctorError("iot-museiq /health no cumple el contrato esperado.")


def _validate_rag_health(payload: dict[str, Any]) -> None:
    required_text = ("collection", "chat_model", "embed_model")
    if payload.get("status") != "ok" or not all(
        isinstance(payload.get(key), str) for key in required_text
    ):
        raise DoctorError("museRAG /health no cumple el contrato esperado.")


def _service_checks(args: argparse.Namespace) -> list[tuple[str, str, Callable[[dict[str, Any]], None]]]:
    requested = set(args.service or ("iot-museiq", "museRAG"))
    checks: list[tuple[str, str, Callable[[dict[str, Any]], None]]] = []
    if "iot-museiq" in requested:
        checks.append(
            (
                "iot-museiq",
                f"{args.iot_url.rstrip('/')}/health",
                _validate_iot_health,
            )
        )
    if "museRAG" in requested:
        checks.append(
            (
                "museRAG",
                f"{args.rag_url.rstrip('/')}/health",
                _validate_rag_health,
            )
        )
    return checks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=f"Diagnostico del nodo distribuido {EXPECTED_NODE_ID}."
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Valida manifiestos y pares sin abrir conexiones HTTP.",
    )
    parser.add_argument(
        "--service",
        action="append",
        choices=("iot-museiq", "museRAG"),
        help="Servicio HTTP a comprobar; se puede repetir. Por defecto comprueba ambos.",
    )
    parser.add_argument(
        "--iot-url",
        default=(
            os.getenv("MUSEIQ_IOT_URL")
            or os.getenv("EXPO_PUBLIC_MUSEIQ_BLE_SIM_URL")
            or "http://127.0.0.1:8787"
        ),
    )
    parser.add_argument(
        "--rag-url",
        default=(
            os.getenv("MUSEIQ_RAG_URL")
            or os.getenv("EXPO_PUBLIC_MUSERAG_URL")
            or "http://127.0.0.1:8000"
        ),
    )
    parser.add_argument("--timeout", type=float, default=5.0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        topology = _check_manifests()
    except DoctorError as exc:
        print(f"FAIL manifest {exc}", file=sys.stderr)
        return 1

    print(f"PASS manifest {topology['node']} -> {', '.join(topology['peers'])}")
    if args.offline:
        return 0

    failed = False
    for service, url, validator in _service_checks(args):
        try:
            validator(_get_json(url, args.timeout))
            print(f"PASS service  {service:<11} {url}")
        except DoctorError as exc:
            failed = True
            print(f"FAIL service  {service:<11} {exc}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

