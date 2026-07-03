from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Sensor, Werte
from web.forms.TempsFilterForm import TempsFilterForm
from web.forms.HumidsFilterForm import HumidsFilterForm
from web.forms.PressFilterForm import PressFilterForm
from web.forms.SensorCreateEditModelForm import SensorCreateEditModelForm
from django.db.models import Max, Min, Avg, Count
from datetime import datetime, timedelta


def _werte_statistik(queryset, feld):
    """Berechnet Min/Max/Durchschnitt/Anzahl für ein Feld des (gefilterten)
    Querysets – liefert die Zahlen für die Statistik-Kacheln der Seiten."""
    return queryset.aggregate(
        minimum=Min(feld),
        maximum=Max(feld),
        durchschnitt=Avg(feld),
        anzahl=Count("id"),
    )


def index(request):
    # return HttpResponse("Hello, world. You're at the web app.")
    return render(request, "web/index.html")


def aktorenchannel(request):
    # Liefert nur die HTML-Seite aus. Die eigentliche Live-Verbindung baut
    # danach das JavaScript im Template per WebSocket auf (siehe aktorenchannel.html).
    return render(request, "web/aktorenchannel.html")


def display_sensors(request):
    queryset = Sensor.objects.all()
    return render(request, "web/sensors.html", {"sensorlist": list(queryset)})


def tempdetails(request, temp_id):
    print(temp_id + "tempdetails")
    queryset = Sensor.objects.get(pk=temp_id)
    return HttpResponse(
        f"""Tempdetails for Sensor-ID {temp_id}:
                         {queryset.raum}, 
                         {queryset.ip},
                         {queryset.code}"""
    )


def edit_sensor_details(request, sensor_id):
    sensor = Sensor.objects.get(pk=sensor_id)

    if request.method == "POST":
        print("GET")
        form = SensorCreateEditModelForm(request.POST, instance=sensor)
        if form.is_valid():
            form.save()
            return redirect("/web/sensors/")
    else:
        print("GET")
        print(sensor_id)
        form = SensorCreateEditModelForm(instance=sensor)
        print(sensor)
        return render(request, "web/sensor_edit.html", {"form": form})


def display_temps(request):
    print("display_temps")
    if request.method == "POST":
        form = TempsFilterForm(request.POST)
        print("display_temps")
        print(form)

        if form.is_valid():
            print(form.cleaned_data)
            lowerVal = form.cleaned_data["lowerVal"]
            if lowerVal is None:
                lowerVal = Werte.objects.aggregate(Min("temperatur"))["temperatur__min"]
                print(lowerVal)

            upperVal = form.cleaned_data["upperVal"]
            if upperVal is None:
                upperVal = Werte.objects.aggregate(Max("temperatur"))["temperatur__max"]
                print(upperVal)

            # if upperVal is None:
            # upperVal = Werte.ob
            vonDate = form.cleaned_data["vonDate"]
            bisDate = form.cleaned_data["bisDate"]
            print(f"{lowerVal}, {upperVal}, {vonDate}, {bisDate}")
            # queryset = Werte.objects.filter(temperatur__lte = form.cleaned_data["upperVal"])
            # queryset = Werte.objects.filter(temperatur__range = (lowerVal, upperVal))
            queryset = Werte.objects.filter(
                datum__gte=vonDate,
                datum__lte=(bisDate + timedelta(days=1)),
                temperatur__lte=upperVal,
                temperatur__gte=lowerVal,
            )

            stats = _werte_statistik(queryset, "temperatur")
            return render(
                request,
                "web/temps.html",
                {
                    "name": "Berg",
                    "tempslist": list(queryset),
                    "form": form,
                    "stats": stats,
                },
            )
        else:
            return HttpResponse(f"Error! {form.errors}")
    else:
        print("GET")
        form = TempsFilterForm()
        form.lowerVal = 4
        queryset = Werte.objects.all()
        tempListe = list(queryset)
        stats = _werte_statistik(queryset, "temperatur")
        return render(
            request,
            "web/temps.html",
            {"form": form, "tempslist": tempListe, "stats": stats},
        )


def display_humids(request):
    print("display_humids")
    if request.method == "POST":
        form = HumidsFilterForm(request.POST)
        print("display_humids_POST")
        print(form)

        if form.is_valid(): #is_valid() kontrolliert InputBox (muss Zahl sein)
            print(form.cleaned_data)
            lowerVal = form.cleaned_data["lowerVal"]
            if lowerVal is None:
                lowerVal = Werte.objects.aggregate(Min("luftfeuchte"))[
                    "luftfeuchte__min"
                ]
                print(lowerVal)

            upperVal = form.cleaned_data["upperVal"]
            if upperVal is None:
                upperVal = Werte.objects.aggregate(Max("luftfeuchte"))[
                    "luftfeuchte__max"
                ]
                print(upperVal)

            vonDate = form.cleaned_data["vonDate"]
            bisDate = form.cleaned_data["bisDate"]
            print(f"{lowerVal}, {upperVal}, {vonDate}, {bisDate}")
            queryset = Werte.objects.filter(
                datum__gte=vonDate,
                datum__lte=(bisDate + timedelta(days=1)),
                luftfeuchte__lte=upperVal,
                luftfeuchte__gte=lowerVal,
            )

            stats = _werte_statistik(queryset, "luftfeuchte")
            return render(
                request,
                "web/humids.html",
                {
                    "name": "Berg",
                    "humidslist": list(queryset),
                    "form": form,
                    "stats": stats,
                },
            )
        else:
            return HttpResponse(f"Error! {form.errors}")
    else:
        print("GET")
        form = HumidsFilterForm()
        form.lowerVal = 4
        queryset = Werte.objects.all()
        humidListe = list(queryset)
        stats = _werte_statistik(queryset, "luftfeuchte")
        return render(
            request,
            "web/humids.html",
            {"form": form, "humidslist": humidListe, "stats": stats},
        )


def display_press(request):
    print("display_press")
    if request.method == "POST":
        form = PressFilterForm(request.POST)
        print("display_press_POST")
        print(form)

        if form.is_valid():
            print(form.cleaned_data)
            lowerVal = form.cleaned_data["lowerVal"]
            if lowerVal is None:
                lowerVal = Werte.objects.aggregate(Min("luftdruck"))["luftdruck__min"]
                print(lowerVal)

            upperVal = form.cleaned_data["upperVal"]
            if upperVal is None:
                upperVal = Werte.objects.aggregate(Max("luftdruck"))["luftdruck__max"]
                print(upperVal)

            vonDate = form.cleaned_data["vonDate"]
            bisDate = form.cleaned_data["bisDate"]
            print(f"{lowerVal}, {upperVal}, {vonDate}, {bisDate}")
            queryset = Werte.objects.filter(
                datum__gte=vonDate,
                datum__lte=(bisDate + timedelta(days=1)),
                luftdruck__lte=upperVal,
                luftdruck__gte=lowerVal,
            )

            stats = _werte_statistik(queryset, "luftdruck")
            return render(
                request,
                "web/press.html",
                {
                    "name": "Berg",
                    "presslist": list(queryset),
                    "form": form,
                    "stats": stats,
                },
            )
        else:
            return HttpResponse(f"Error! {form.errors}")
    else:
        print("GET")
        form = PressFilterForm()
        form.lowerVal = 4
        queryset = Werte.objects.all()
        pressListe = list(queryset)
        stats = _werte_statistik(queryset, "luftdruck")
        return render(
            request,
            "web/press.html",
            {"form": form, "presslist": pressListe, "stats": stats},
        )


def new_sensor(request):
    if request.method == "POST":
        form = SensorCreateEditModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/web/sensors/")
        else:
            return HttpResponse("Error")
    else:
        print("GET")
        form = SensorCreateEditModelForm()
        return render(request, "web/sensor_edit.html", {"form": form})
