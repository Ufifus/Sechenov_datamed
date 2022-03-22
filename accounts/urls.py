from django.urls import path, include
from .views import *

urlpatterns = [
    path('login', Login.as_view(), name='log-in'),
    path('logout', LogoutView.as_view(), name='log-out'),
    path('registration', SignUp.as_view(), name='sigh-up')
]