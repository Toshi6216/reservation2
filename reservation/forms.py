from django import forms
from .models import *
from datetime import time
from django.forms import widgets
import datetime

class EventForm(forms.ModelForm):
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Event
        # fields = '__all__'
        fields = [

            "event_date",
            "start_time",
            "end_time",
            "event_title", 
            "event_detail",
        ]

class SearchForm(forms.Form):
    keyword = forms.CharField(
        label='', 
        max_length=50, 
        required=False,
        )

        
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ("group_name", "group_detail")

        
