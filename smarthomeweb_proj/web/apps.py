import os
import sys

from django.apps import AppConfig


class WebConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "web"

    def ready(self):
        # Den MQTT-Client nur starten, wenn der Entwicklungs-Webserver läuft –
        # NICHT bei Befehlen wie migrate / makemigrations / shell / Tests.
        if "runserver" not in sys.argv:
            return
        # Der Auto-Reloader ruft ready() zweimal auf (Eltern- + Kindprozess).
        # RUN_MAIN=="true" ist nur der echte Server-Kindprozess; bei --noreload
        # gibt es keinen Kindprozess (RUN_MAIN dann nicht gesetzt).
        if os.environ.get("RUN_MAIN") == "true" or "--noreload" in sys.argv:
            from web import mqtt_client

            mqtt_client.start()
