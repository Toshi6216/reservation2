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
            "event_title", 
            "event_detail",
            "event_date",
            "start_time",
            "end_time",
    
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

        
class ContactForm(forms.Form):
    subject = forms.CharField(label='件名', max_length=100)
    send_to = forms.EmailField(label='Email', help_text='※ご確認の上、正しく入力してください。')
    message = forms.CharField(label='メッセージ', widget=forms.Textarea)
    myself = forms.BooleanField(label='同じ内容を受け取る', required=False)