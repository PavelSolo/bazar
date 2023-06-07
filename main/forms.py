from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from multiupload.fields import MultiFileField
from .models import *
from django.forms import ModelForm, inlineformset_factory, ClearableFileInput


class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-input-reg', 'placeholder': 'Email' }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input-reg', 'placeholder': 'Пароль'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input-reg', 'placeholder':'Повтор пароля'}))

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input-reg', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input-reg', 'placeholder': 'Пароль'}))

    class Meta:
        model = User
        fields = ('username', 'password')


class UpdateUserForm(forms.ModelForm):
    email = forms.EmailField(label='Электронная почта:', widget=forms.EmailInput())
    first_name = forms.CharField(label='Имя:', widget=forms.TextInput())
    last_name = forms.CharField(label='Фамилия:', widget=forms.TextInput())
    phonenumber = forms.CharField(label='Номер телефона:')
    city = forms.CharField(label='Город:', widget=forms.TextInput())

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'city', 'phonenumber']


class ProductForm(forms.ModelForm):
    photos = MultiFileField(min_num=1, max_num=10, max_file_size=1024*1024*5, required=False)  # Максимум 10 фотографий размером до 5 МБ

    class Meta:
        model = Product
        fields = ['name', 'cost', 'category', 'description', 'city']

    def clean_photos(self):
        photos = self.cleaned_data.get('photos')
        if photos and len(photos) > 10:
            raise forms.ValidationError('Максимальное количество фотографий - 10')
        return photos