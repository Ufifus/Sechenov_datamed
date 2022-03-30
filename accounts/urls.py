from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import Login, Registation, activate_user

urlpatterns = [
    path('login', Login.as_view(), name='log-in'),
    path('logout', LogoutView.as_view(), name='log-out'),
    path('registration', Registation.as_view(), name='sigh-up'),
    path('activate_user/<uid64>/<token>', activate_user, name='activate')  # Активация профиля
]