from django import forms
from django.forms import fields
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name',
            'last_name',
            'phone', 
            'email', 
            'address',
            'zip_code',
            'complement',
            'order_note'    
        ]