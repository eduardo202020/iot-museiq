import struct
import time
import ubluetooth
from machine import Pin

# BLE UUIDs
SERVICE_UUID = ubluetooth.UUID(0xA100)
CHAR_UUID_RX = ubluetooth.UUID(0xA101)  # App escribe aqui
CHAR_UUID_TX = ubluetooth.UUID(0xA102)  # ESP32 responde aqui

# BLE events
_IRQ_CENTRAL_CONNECT = 1
_IRQ_CENTRAL_DISCONNECT = 2
_IRQ_GATTS_WRITE = 3
LED1_GPIO = 2
LED2_GPIO = 15
BUTTON_GPIO = 0
BUTTON_DEBOUNCE_MS = 180

CURRENT_BLE = None


def _to_hex(data):
    return "".join("{:02x}".format(b) for b in data)


def _adv_payload(name, service_uuid_16):
    payload = bytearray()

    def _append(ad_type, value):
        payload.extend(struct.pack("BB", len(value) + 1, ad_type) + value)

    # LE General Discoverable + BR/EDR not supported
    _append(0x01, b"\x06")
    _append(0x09, name.encode("utf-8"))
    _append(0x03, struct.pack("<H", service_uuid_16))  # Complete List of 16-bit UUIDs
    return payload


class BLEBidirectional:
    def __init__(self):
        self._ble = ubluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        self._connections = set()
        self._last_rx = b""
        self._led1 = None
        self._led2 = None
        self._setup_led()
        self._register_services()

    def _setup_led(self):
        try:
            self._led1 = Pin(LED1_GPIO, Pin.OUT)
            self._led1.value(0)
            print("LED1 configurado en GPIO{}".format(LED1_GPIO))
        except Exception:
            self._led1 = None
            print("No se pudo configurar LED1 en GPIO{}".format(LED1_GPIO))

        try:
            self._led2 = Pin(LED2_GPIO, Pin.OUT)
            self._led2.value(0)
            print("LED2 configurado en GPIO{}".format(LED2_GPIO))
        except Exception:
            self._led2 = None
            print("No se pudo configurar LED2 en GPIO{}".format(LED2_GPIO))

    def _register_services(self):
        service = (
            SERVICE_UUID,
            (
                (CHAR_UUID_RX, ubluetooth.FLAG_WRITE | ubluetooth.FLAG_WRITE_NO_RESPONSE),
                (CHAR_UUID_TX, ubluetooth.FLAG_READ | ubluetooth.FLAG_NOTIFY),
            ),
        )
        ((self._handle_rx, self._handle_tx),) = self._ble.gatts_register_services((service,))
        self._ble.gatts_write(self._handle_tx, b"Hola desde ESP32")

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, addr_type, addr = data
            self._connections.add(conn_handle)
            addr_str = ":".join("{:02x}".format(b) for b in bytes(addr))
            print("Central conectado:", addr_str, "type", addr_type)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)
            addr_str = ":".join("{:02x}".format(b) for b in bytes(addr))
            print("Central desconectado:", addr_str, "type", addr_type)
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._handle_rx:
                value = self._ble.gatts_read(self._handle_rx)
                self._last_rx = value
                try:
                    text = value.decode("utf-8", "ignore")
                except Exception:
                    text = ""
                print("App escribio:", text)
                print("App escribio (hex):", _to_hex(value))
                if not self._handle_command(text):
                    self.send_text("Recibido: " + text)

    def _handle_command(self, text):
        cmd = text.strip().upper()
        if cmd == "LED1_ON":
            self._set_led(1, True)
            return True
        if cmd == "LED1_OFF":
            self._set_led(1, False)
            return True
        if cmd == "LED2_ON":
            self._set_led(2, True)
            return True
        if cmd == "LED2_OFF":
            self._set_led(2, False)
            return True
        # Compatibilidad con comandos anteriores
        if cmd == "LED_PIN36_ON":
            self._set_led(1, True)
            return True
        if cmd == "LED_PIN36_OFF":
            self._set_led(1, False)
            return True
        return False

    def _set_led(self, led_index, on):
        led = self._led1 if led_index == 1 else self._led2
        gpio = LED1_GPIO if led_index == 1 else LED2_GPIO

        if led is None:
            msg = "ERROR_LED{}: GPIO{} no disponible".format(led_index, gpio)
            print(msg)
            self.send_text(msg)
            return

        led.value(1 if on else 0)
        state = "ON" if on else "OFF"
        msg = "LED{}_GPIO{}_{}".format(led_index, gpio, state)
        print("LED{} {} en GPIO{}".format(led_index, state, gpio))
        self.send_text(msg)

    def _advertise(self):
        payload = _adv_payload("ESP32-Bidir", 0xA100)
        try:
            self._ble.gap_advertise(500_000, adv_data=payload, connectable=True)
            print("Advertising (bidireccional, connectable=True)")
        except TypeError:
            self._ble.gap_advertise(500_000, adv_data=payload)
            print("Advertising (modo compatibilidad)")

    def send_text(self, text):
        if isinstance(text, str):
            data = text.encode("utf-8")
        else:
            data = bytes(text)
        self._ble.gatts_write(self._handle_tx, data)
        for conn in tuple(self._connections):
            try:
                self._ble.gatts_notify(conn, self._handle_tx)
            except OSError:
                pass
        print("Mensaje enviado (hex):", _to_hex(data))

    def start(self):
        self._advertise()

    def stop(self):
        self._ble.gap_advertise(None)
        print("Advertising detenido")


def send_text(text):
    if CURRENT_BLE is None:
        print("BLE no inicializado")
        return
    CURRENT_BLE.send_text(text)


def main():
    global CURRENT_BLE
    print("Iniciando BLE bidireccional...")
    CURRENT_BLE = BLEBidirectional()
    CURRENT_BLE.start()

    # Boton dedicado para enviar evento BLE (activo en LOW con PULL_UP)
    boton = Pin(BUTTON_GPIO, Pin.IN, Pin.PULL_UP)
    last_state = boton.value()
    last_press_ms = 0
    print("Boton listo en GPIO{} (estado inicial={})".format(BUTTON_GPIO, last_state))

    while True:
        time.sleep_ms(50)
        state = boton.value()
        now = time.ticks_ms()
        if state != last_state:
            # Debounce por flanco
            if time.ticks_diff(now, last_press_ms) > BUTTON_DEBOUNCE_MS:
                if state == 0:
                    CURRENT_BLE.send_text("BOTON_GPIO{}_PRESS".format(BUTTON_GPIO))
                    print("Boton presionado en GPIO{}".format(BUTTON_GPIO))
                else:
                    CURRENT_BLE.send_text("BOTON_GPIO{}_RELEASE".format(BUTTON_GPIO))
                    print("Boton liberado en GPIO{}".format(BUTTON_GPIO))
                last_press_ms = now
        last_state = state


if __name__ == "__main__":
    main()
