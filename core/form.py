from django import forms
from django.core.exceptions import ValidationError
from .models import FeedbackModel


class FeedbackForm(forms.Form):
    feedback = forms.CharField(widget=forms.TextInput())


class CheckoutForm(forms.Form):
    address = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',

    }))

    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',

    }))

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        if phone[:2] != '09':
            raise ValidationError('Phone number must start with 09')
        if len(phone) != 11:
            raise ValidationError('Phone number must be 11')

        return phone
