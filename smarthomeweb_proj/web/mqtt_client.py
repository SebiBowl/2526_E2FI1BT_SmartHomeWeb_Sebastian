"""
MQTT-Anbindung für SmartHomeWeb.

Was diese Datei macht:
  - verbindet sich (im Hintergrund) mit dem MQTT-Broker,
  - abonniert die Sensor-Topics des ESP32,
  - schiebt jeden empfangenen Messwert LIVE an die Browser (WebSocket-Gruppe),
  - sammelt Temperatur/Feuchte/Druck und speichert einen kompletten Satz in der DB.

Läuft in einem Hintergrund-Thread (paho-mqtt), der beim Serverstart über
web/apps.py gestartet wird. Der Thread darf NICHT direkt async_to_sync(group_send)
benutzen (andere Event-Loop!) – deshalb nutzen wir run_coroutine_threadsafe und
die vom Consumer gemerkte Server-Loop (siehe set_server_loop / _broadcast).
"""

import asyncio

import paho.mqtt.client as mqtt
from channels.layers import get_channel_layer
from django.conf import settings

# Name der WebSocket-Gruppe – muss zum AktorenConsumer passen.
GROUP = "aktoren"

# Zuordnung MQTT-Messgröße -> (Anzeigename, Einheit)
GROESSEN = {
    "temperature": ("Temperatur", "°C"),
    "humidity": ("Luftfeuchte", "%"),
    "pressure": ("Luftdruck", "hPa"),
}

# --- interner Zustand ---------------------------------------------------------
_client = None            # der paho-Client
_started = False          # verhindert doppelten Start
_server_loop = None       # Event-Loop des Webservers (vom Consumer gesetzt)
_buffer = {}              # device_id -> {"temperature":.., "humidity":.., "pressure":..}


def set_server_loop(loop):
    """Vom Consumer beim Verbinden aufgerufen: merkt sich die Event-Loop des
    Servers, damit der MQTT-Thread darüber Live-Nachrichten schicken kann."""
    global _server_loop
    _server_loop = loop


def _broadcast(payload):
    """Schickt ein payload-dict an ALLE verbundenen Browser (WebSocket-Gruppe)."""
    loop = _server_loop
    if loop is None:
        return  # noch kein Browser/Consumer aktiv -> nichts zu senden
    layer = get_channel_layer()
    coro = layer.group_send(GROUP, {"type": "aktor.event", "payload": payload})
    # run_coroutine_threadsafe: aus unserem Thread sicher in die Server-Loop.
    asyncio.run_coroutine_threadsafe(coro, loop)


def _speichere_datensatz(device_id, werte):
    """Speichert einen kompletten Messsatz (Temp/Feuchte/Druck) in der DB."""
    from django.db import close_old_connections
    from django.utils import timezone
    from web.models import Sensor, Werte

    close_old_connections()  # im Thread eine frische DB-Verbindung sicherstellen
    try:
        # Sensor anhand der Geräte-ID finden oder neu anlegen.
        sensor, _ = Sensor.objects.get_or_create(
            code=device_id,
            defaults={"raum": device_id, "ip": ""},
        )
        Werte.objects.create(
            sen=sensor,
            temperatur=werte["temperature"],
            luftfeuchte=werte["humidity"],
            luftdruck=werte["pressure"],
            datum=timezone.now(),
        )
    finally:
        close_old_connections()


def _handle_message(topic, payload_text):
    """Verarbeitet EINE MQTT-Nachricht. Getrennt gehalten, damit gut testbar."""
    teile = topic.split("/")     # z.B. smarthome/sensor/feather-livingroom/temperature
    if len(teile) < 2:
        return
    device_id = teile[-2]
    groesse = teile[-1]          # temperature / humidity / pressure
    if groesse not in GROESSEN:
        return
    try:
        wert = float(payload_text)
    except (ValueError, TypeError):
        return

    name, einheit = GROESSEN[groesse]

    # (1) Sofort live an die Browser schicken.
    _broadcast({
        "typ": "messwert",
        "groesse": groesse,
        "name": name,
        "einheit": einheit,
        "wert": wert,
        "device": device_id,
    })

    # (2) Werte sammeln; sobald alle drei da sind -> als ein Datensatz speichern.
    buf = _buffer.setdefault(device_id, {})
    buf[groesse] = wert
    if all(g in buf for g in GROESSEN):
        _speichere_datensatz(device_id, buf)
        _broadcast({
            "typ": "info",
            "text": f"Kompletter Datensatz von '{device_id}' gespeichert.",
        })
        _buffer[device_id] = {}


# --- paho-Callbacks (Callback-API Version 2) ----------------------------------
def _on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        client.subscribe(settings.MQTT_TOPIC)
        print(f"[MQTT] verbunden – abonniere '{settings.MQTT_TOPIC}'")
    else:
        print(f"[MQTT] Verbindung abgelehnt (reason_code={reason_code})")


def _on_message(client, userdata, msg):
    try:
        _handle_message(msg.topic, msg.payload.decode("utf-8", "replace"))
    except Exception as e:
        print("[MQTT] Fehler beim Verarbeiten einer Nachricht:", e)


def _on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print(f"[MQTT] getrennt (reason_code={reason_code}) – reconnect läuft im Hintergrund")


def start():
    """Startet den MQTT-Hintergrund-Client – einmalig und NICHT blockierend."""
    global _client, _started
    if _started:
        return
    if not getattr(settings, "MQTT_ENABLED", False):
        print("[MQTT] deaktiviert (MQTT_ENABLED = False)")
        return
    _started = True

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if settings.MQTT_USERNAME:
        client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    client.on_connect = _on_connect
    client.on_message = _on_message
    client.on_disconnect = _on_disconnect
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    print(f"[MQTT] verbinde mit {settings.MQTT_BROKER}:{settings.MQTT_PORT} …")
    # connect_async + loop_start blockieren NICHT und versuchen bei Bedarf im
    # Hintergrund immer wieder zu verbinden -> Django startet auch OHNE Broker.
    client.connect_async(settings.MQTT_BROKER, settings.MQTT_PORT, keepalive=60)
    client.loop_start()
    _client = client
