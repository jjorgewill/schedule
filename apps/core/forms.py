from django import forms

from apps.core import models
from django.forms.widgets import TextInput


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.CharField(required=True)
    phone = forms.CharField(required=False)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = models.Profile
        exclude = ("user",)
        widgets = {
            'color': TextInput(attrs={'type':'color'})
        }


class HolidayForm(forms.ModelForm):

    class Meta:
        model = models.Holiday
        fields = ['day']


class ProfessionForm(forms.ModelForm):

    class Meta:
        model = models.Profession
        fields = ['name','abbreviation']


class TurnForm(forms.ModelForm):

    class Meta:
        model = models.Turn
        fields = ['name','hour']


class StatusForm(forms.ModelForm):

    class Meta:
        model = models.Status
        fields = ['name']


class HourForm(forms.ModelForm):

    class Meta:
        model = models.Hour
        fields = ['start_time','end_time']
        widgets = {
            'start_time': TextInput(attrs={'type': 'time'}),
            'end_time': TextInput(attrs={'type': 'time'}),
        }


class EventForm(forms.ModelForm):
    date_start = forms.DateField(widget=forms.HiddenInput())
    date_end = forms.DateField(widget=forms.HiddenInput())
    profile = forms.ModelChoiceField(queryset=models.Profile.objects.filter(is_removed=False).exclude(user__is_staff=True))
    class Meta:
        model = models.Event
        fields = ['turn','profile']

