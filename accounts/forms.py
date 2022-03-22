from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class UserLoginForm(AuthenticationForm):

    username = forms.CharField(
        label='Логин'
    )

    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    error_messages = {
        'invalid_login':
            "Пожайлуста введите конкретный логин и пароль",

        'inactive': "Данный аккаунт недоступен",
    }


class UserRegisterForm(UserCreationForm):

  username = forms.CharField(
      label='Логин'
  )

  first_name = forms.CharField(
      label='Имя'
  )

  email = forms.EmailField()

  password1 = forms.CharField(
      label="Пароль",
      strip=False,
      widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
      # help_text=password_validation.password_validators_help_text_html(),
  )

  password2 = forms.CharField(
      label="Повторите пароль",
      widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
      strip=False,
  )

  error_messages = {
      'password_mismatch': 'Пароли не совпадают',
  }

  class Meta:
      model = User
      fields = ['username', 'email', 'first_name', 'password1', 'password2']





