from django import forms
from django.forms import fields
from django.forms.widgets import PasswordInput
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=PasswordInput(
        {
            'placeholder': 'Sua senha',
        }
    ))
    confirm_password = forms.CharField(widget=PasswordInput(
        {
            'placeholder': 'Repita sua senha',
        }
    ))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs['placeholder'] = 'Digite seu nome'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Digite seu sobrenome'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Digite seu telefone'
        self.fields['email'].widget.attrs['placeholder'] = 'Digite seu email'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "As senhas não coincidem"
            )


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('zip_code', 'address', 'complement', 'state', 'city', 'country')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'