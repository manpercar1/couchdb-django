#encoding:utf-8
from django import forms

class BusquedaEquipo(forms.Form):
    nombre = forms.CharField(label="Nombre", required=True)