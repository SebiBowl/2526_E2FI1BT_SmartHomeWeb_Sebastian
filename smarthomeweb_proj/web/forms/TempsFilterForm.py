from django import forms
from datetime import datetime, timedelta


"""Beispiel mit reinem Form. (Nicht ModelForm.)"""


class TempsFilterForm(forms.Form):
    lowerVal = forms.DecimalField(
        widget=forms.NumberInput(attrs={"placeholder": "z. B. 18.0", "step": "0.1"}),
        label="Minimum (°C)",
        help_text="Leer = kein unteres Limit",
        required=False,
        max_value=60.0,
        min_value=-50.0,
        max_digits=3,
        decimal_places=1,
    )

    upperVal = forms.DecimalField(
        widget=forms.NumberInput(attrs={"placeholder": "z. B. 24.0", "step": "0.1"}),
        label="Maximum (°C)",
        help_text="Leer = kein oberes Limit",
        max_value=60.0,
        min_value=-50.0,
        max_digits=3,
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
