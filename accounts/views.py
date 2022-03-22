from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import FormView, CreateView
from django.core.exceptions import ImproperlyConfigured

from .forms import UserRegisterForm, UserLoginForm



class Login(LoginView):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'


class SignUp(CreateView):
    form_class = UserRegisterForm
    success_url = 'login'
    template_name = 'accounts/registration.html'
    success_message = "Вы удачно зарегистрировались"

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return self.success_url  # success_url may be lazy



