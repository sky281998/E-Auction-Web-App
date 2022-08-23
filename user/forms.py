from django import forms
from django.contrib.auth.models import User
from .models import Message


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password')


class DateForm(forms.Form):
    datepicker = forms.DateField()


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['message']
