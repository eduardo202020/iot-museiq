import struct
import time
import ubluetooth

# Configuracion del beacon
ROOM_ID = "SALA_1"
BEACON_NODE = 2  # Identificador del beacon dentro de la sala (1..N)
FW_VERSION = (1, 0)
BATTERY_MV = 3700  # Valor estimado; actualiza si tienes medicion real
BEACON_ID = "{}-B{:02d}".format(ROOM_ID, BEACON_NODE)
ADV_INTERVAL_US = 500_000  # 500 ms (recomendado para produccion)
TX_POWER_DBM = -12  # -4 dBm para distancias largas (4-10 metros); usar -12 dBm para cortas
# Parametro de propagacion para RSSI: n=2.5 para espacios libres de obstaculos

# Logs: usa LOG_VERBOSE=True solo para depurar
LOG_INFO = True
LOG_VERBOSE = False
LOG_HEARTBEAT_EVERY = 2  # cada 2 ciclos = 10 s

# Estructura del Service Data (UUID 0xA00A):
# - ROOM_ID (6 bytes): ID de la sala en UTF-8 (ej. "SALA_2")
# - BEACON_NODE (1 byte): Numero del beacon en la sala (1-255)
# - FW_VERSION (2 bytes): Major + Minor
# - TX_POWER_DBM (1 byte signed): Potencia de transmision calibrada (-128 a 127)
# - BATTERY_MV (2 bytes): Nivel de bateria en mV (0-65535)
# Total Service Data: 12 bytes

SERVICE_UUID_16 = 0xA00A  # UUID 16-bit reservado para datos del beacon
CHAR_UUID_ID = 0xA00B
CHAR_UUID_TX = 0xA00C

_IRQ_CENTRAL_CONNECT = 1
_IRQ_CENTRAL_DISCONNECT = 2
_IRQ_GATTS_WRITE = 3


def _advertising_payload(name=None, service_uuid_16=None, service_data=None, tx_power=None):
    payload = bytearray()

    def _append(ad_type, value):
        payload.extend(struct.pack("BB", len(value) + 1, ad_type) + value)

    # Flags: LE General Discoverable + BR/EDR not supported
    _append(0x01, b"\x06")

    if name:
        _append(0x09, name.encode("utf-8"))

    if service_data is not None and service_uuid_16 is not None:
        # Service Data - 16-bit UUID (0x16)
        value = struct.pack("<H", service_uuid_16) + service_data
        _append(0x16, value)

    if tx_power is not None:
        _append(0x0A, struct.pack("b", tx_power))

    return payload


def _log_info(message):
    if LOG_INFO:
        print(message)


def _log_verbose(message):
    if LOG_VERBOSE:
        print(message)


class BLEBeacon:
    def __init__(self, beacon_id):
        self._ble = ubluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        self._beacon_id = beacon_id
        self._connections = set()
        self._register_services()

    def _register_services(self):
        service = (
            ubluetooth.UUID(SERVICE_UUID_16),
            (
                (ubluetooth.UUID(CHAR_UUID_ID), ubluetooth.FLAG_READ),
                (ubluetooth.UUID(CHAR_UUID_TX), ubluetooth.FLAG_READ),
            ),
        )
        ((self._handle_id, self._handle_tx),) = self._ble.gatts_register_services((service,))
        self._ble.gatts_write(self._handle_id, self._beacon_id.encode("utf-8"))
        self._ble.gatts_write(self._handle_tx, struct.pack("b", TX_POWER_DBM))

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, addr_type, addr = data
            self._connections.add(conn_handle)
            addr_str = ":".join("{:02x}".format(b) for b in bytes(addr))
            _log_verbose("Central conectado: {} (type {})".format(addr_str, addr_type))
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)
            addr_str = ":".join("{:02x}".format(b) for b in bytes(addr))
            _log_verbose("Central desconectado: {} (type {})".format(addr_str, addr_type))
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            _log_verbose("GATTS write: conn={} handle={}".format(conn_handle, value_handle))

    def _advertise(self):
        room_bytes = ROOM_ID.encode("utf-8")
        fw_major, fw_minor = FW_VERSION
        # Incluir TX_POWER_DBM en el Service Data junto con sala y beacon
        extra = struct.pack("<BBBbH", BEACON_NODE, fw_major, fw_minor, TX_POWER_DBM, BATTERY_MV)
        service_data = room_bytes + extra
        adv_data = _advertising_payload(
            name=ROOM_ID,
            service_uuid_16=SERVICE_UUID_16,
            service_data=service_data,
            tx_power=TX_POWER_DBM,
        )

        try:
            self._ble.gap_advertise(ADV_INTERVAL_US, adv_data=adv_data, connectable=True)
            _log_verbose("Advertising en curso (connectable=True)")
        except TypeError:
            # Compatibilidad con firmwares que no soportan connectable
            self._ble.gap_advertise(ADV_INTERVAL_US, adv_data=adv_data)
            _log_verbose("Advertising en curso (modo compatibilidad)")

        interval_ms = ADV_INTERVAL_US / 1000
        _log_verbose("Log TX: potencia={} dBm, intervalo={} ms".format(TX_POWER_DBM, int(interval_ms)))
        _log_verbose("Beacon emitiendo: ID = {}".format(self._beacon_id))
        _log_verbose("Service Data: Sala={}, Beacon={}, TxPower={}dBm, Battery={}mV".format(
            ROOM_ID, BEACON_NODE, TX_POWER_DBM, BATTERY_MV))

    def start(self):
        _log_info("Advertising iniciado")
        self._advertise()

    def stop(self):
        self._ble.gap_advertise(None)
        _log_info("Advertising detenido")


def main():
    _log_info("Iniciando beacon BLE...")
    beacon = BLEBeacon(BEACON_ID)
    beacon.start()
    
    counter = 0
    # Mantener el beacon activo
    while True:
        time.sleep(5)
        counter += 1
        if counter % LOG_HEARTBEAT_EVERY == 0:
            _log_info("Heartbeat: {} seg - Beacon activo".format(counter * 5))
        # Re-anunciar cada 25 segundos para evitar timeouts
        if counter % 5 == 0:
            _log_verbose("Re-advertising (keepalive)...")
            beacon._advertise()


if __name__ == "__main__":
    main()
