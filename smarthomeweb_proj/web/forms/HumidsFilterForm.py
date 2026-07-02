from django import forms
from datetime import datetime, timedelta


"""Beispiel mit reinem Form. (Nicht ModelForm.)"""


class HumidsFilterForm(forms.Form):
    lowerVal = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                "class": "form-control form-control-lg",
                "aria-label": ".form-control-lg example",
            }
        ),
        label="Bitte untere Grenze eingeben:",
        required=False,
        max_value=60.0,
        min_value=-50.0,
        max_digits=3,
        decimal_places=1,
    )

    upperVal = forms.DecimalField(
        label="Bitte obere Grenze eingeben:",
        widget=forms.NumberInput(attrs={"class": "form-control form-control-lg"}),
        max_value=60.0,
        min_value=-50.0,
        max_digits=3,
        decimal_places=1,
        required=False,
        # initial=23.0
    )

    vonDate = forms.DateField(
        initial=datetime.today().replace(year=2022) - timedelta(days=5),
        widget=forms.DateInput(
            attrs={"class": "form-control form-control-lg"}, format="%d.%m.%Y"
        ),
        label="Bitte das Datum eingeben, ab wann die Feuchtigkeitswerte angezeigt werden sollen. (Default = vor 5 Tagen) ",
        required=False,
        input_formats=["%d.%m.%Y"],
    )

    bisDate = forms.DateField(
        initial=datetime.today().replace(year=2022),
        widget=forms.DateInput(
            attrs={"class": "form-control form-control-lg"}, format="%d.%m.%Y"
        ),
        label="Bitte das letzte Datum eingeben, bis zu dem Die Feuchtigkeitswerte angezeigt werden sollen. (Default = heute)",
        input_formats=["%d.%m.%Y"],
        required=False,
    )
