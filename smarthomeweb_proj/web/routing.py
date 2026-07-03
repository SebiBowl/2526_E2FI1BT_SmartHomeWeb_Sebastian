"""
WebSocket-URL-Routing für die App "web".

Das ist das Gegenstück zu urls.py – nur eben für WebSocket-Verbindungen statt
für normale Seiten. Konvention: WebSocket-Adressen beginnen mit "ws/", damit sie
klar von den HTTP-Seiten getrennt sind.
"""

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # Der Browser verbindet sich später mit:  ws://<host>/ws/aktoren/
    re_path(r"^ws/aktoren/$", consumers.AktorenConsumer.as_asgi()),
]
