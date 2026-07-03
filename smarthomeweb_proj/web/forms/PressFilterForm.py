from django import forms
from datetime import datetime, timedelta


"""Beispiel mit reinem Form. (Nicht ModelForm.)"""


class PressFilterForm(forms.Form):
    lowerVal = forms.DecimalField(
        widget=forms.NumberInput(attrs={"placeholder": "z. B. 990", "step": "0.1"}),
        label="Minimum (hPa)",
        help_text="Leer = kein unteres Limit",
        required=False,
        max_value=1200.0,
        min_value=800.0,
        max_digits=5,
        decimal_places=1,
    )

    upperVal = forms.DecimalField(
        widget=forms.NumberInput(attrs={"placeholder": "z. B. 1030", "step": "0.1"}),
        label="Maximum (hPa)",
        help_text="Leer = kein oberes Limit",
        max_value=1200.0,
        min_value=800.0,
        max_digits=5,
        decimal_places=1,
        required=False,
    )

    vonDate = forms.DateField(
        initial=datetime.today() - timedelta(days=5),
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        label="Von",
        required=False,
        input_formats=["%Y-%m-%d"],
    )

    bisDate = forms.DateField(
        initial=datetime.today(),
        widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        label="Bis",
        input_formats=["%Y-%m-%d"],
        required=False,
    )
