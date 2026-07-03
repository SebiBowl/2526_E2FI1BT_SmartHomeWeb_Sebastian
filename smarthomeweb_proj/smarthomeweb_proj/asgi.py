"""
ASGI config for smarthomeweb_proj project.

Früher hat diese Datei nur ganz normales HTTP-Django ausgeliefert.
Jetzt entscheidet sie anhand des Protokolls, WER eine Anfrage bearbeitet:
  - "http"      -> das gewohnte Django (alle bisherigen Seiten, unverändert)
  - "websocket" -> Django Channels (unsere neue, dauerhaft offene Live-Verbindung)

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smarthomeweb_proj.settings")

# WICHTIG: Zuerst das normale Django initialisieren (damit Apps/Models geladen sind),
# BEVOR wir eigenen App-Code (consumers/routing) importieren, der davon abhängt.
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from web.routing import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        # Normale Webseiten laufen weiter über das klassische Django – nichts ändert sich.
        "http": django_asgi_app,
        # WebSocket-Verbindungen gehen an unsere Consumer (siehe web/routing.py).
        #   AllowedHostsOriginValidator: lässt nur Verbindungen von erlaubten Hosts zu (Schutz).
        #   AuthMiddlewareStack:         stellt den eingeloggten User auch im WebSocket bereit.
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
