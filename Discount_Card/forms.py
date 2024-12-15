from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.core.validators import RegexValidator

class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Username'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@example.com'}),
        label='Email'
    )
    phone_number = forms.CharField(
        required=True,
        max_length=14,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+20xxxxxxxxxx'}),
        validators=[RegexValidator(regex=r'^\+20\d{10}$')],
        label='Phone Number'
    )
    first_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mohammed'}),
        label='First Name'
    )
    last_name = forms.CharField(
    required=True,
    max_length=30,
    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mohammed Family'}),
    label='Last Name'
    )
    password1 = forms.CharField(
        label = "Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
    label = "Confirm Password",
    widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2' )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists(): 
            raise forms.ValidationError("This username is already taken.")
        return username