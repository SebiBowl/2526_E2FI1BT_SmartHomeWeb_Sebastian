"""
Consumer = das WebSocket-Gegenstück zu einer View.

Dieser Consumer verbindet die Browser mit den Live-Sensordaten:
  - Beim Verbinden merkt er sich die Event-Loop des Servers, damit der
    MQTT-Hintergrund-Thread (web/mqtt_client.py) ihm Nachrichten schicken kann.
  - Alle Browser sind in der Gruppe "aktoren". Kommt vom MQTT-Thread ein
    group_send herein, ruft Channels hier die Methode aktor_event() auf, die
    die Daten an genau diesen Browser weiterreicht.
"""

import asyncio
import json

from channels.generic.websocket import AsyncWebsocketConsumer


class AktorenConsumer(AsyncWebsocketConsumer):
    GROUP = "aktoren"

    async def connect(self):
        # Event-Loop des Servers merken, damit der MQTT-Thread darüber
        # Live-Nachrichten an die Browser schicken kann.
        from web import mqtt_client
        mqtt_client.set_server_loop(asyncio.get_running_loop())

        # Diesen Browser der Gruppe "aktoren" hinzufügen und Verbindung annehmen.
        await self.channel_layer.group_add(self.GROUP, self.channel_name)
        await self.accept()

        # Kurze Begrüßung nur an diesen einen Browser.
        await self.send(text_data=json.dumps({
            "typ": "info",
            "text": "Verbunden – warte auf Live-Sensordaten …",
        }))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.GROUP, self.channel_name)

    async def aktor_event(self, event):
        # Gruppen-Handler: wird aufgerufen, wenn irgendwo
        # group_send(..., {"type": "aktor.event", "payload": ...}) ausgelöst wird
        # (bei uns aus dem MQTT-Thread). Nutzdaten an diesen Browser weiterreichen.
        await self.send(text_data=json.dumps(event["payload"]))
