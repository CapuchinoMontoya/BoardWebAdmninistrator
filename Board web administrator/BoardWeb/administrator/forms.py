from django import forms
from django.forms.widgets import NumberInput
from django.forms import DateField, ModelForm
from .models import Room, Reservation

#Formularios que al final no use
class createMeetingForm(ModelForm):
    class Meta:
        model = Reservation
        fields = ['startDate', 'endDate']
        widgets = {
            'startDate': forms.DateInput(attrs={'type': 'datetime-local'}),
            'endDate': forms.DateInput(attrs={'type': 'datetime-local'}),
        }

class detailsMeetingForm(ModelForm):
    class Meta:
        model = Reservation
        fields = ['startDate', 'endDate']
        widgets = {
            'startDate': forms.DateInput(attrs={'type': 'datetime-local'}),
            'endDate': forms.DateInput(attrs={'type': 'datetime-local'}),
        }
