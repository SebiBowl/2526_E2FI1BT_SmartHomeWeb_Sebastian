from django.db import models
from django.utils import timezone


class Sensor(models.Model):
    raum = models.CharField(max_length=45)
    ip = models.CharField(max_length=45)
    code = models.TextField()

    class Meta:
        managed = True
        db_table = "sensor"


class Werte(models.Model):
    sen = models.ForeignKey(Sensor, on_delete=models.DO_NOTHING, default=1)
    luftdruck = models.FloatField()
    luftfeuchte = models.FloatField()
    temperatur = models.FloatField()
    datum = models.DateTimeField()

    class Meta:
        managed = True
        db_table = "werte"
