from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('search_engine.urls')),  # http://127.0.0.1:8000/
    path('admin/', admin.site.urls),  # http://127.0.0.1:8000/admin
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('celery-progress/', include('celery_progress.urls'))
]
