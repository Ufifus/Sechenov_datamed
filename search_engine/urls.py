from django.urls import path
from .views import *

urlpatterns = [
    path('', SearchPubmedView.as_view(), name='search_pubmed_page'),  # http://127.0.0.1:8000/
    path('stop/<slug:task_id>', StopTask.as_view(), name='stop_task'),
    path('local/', SearchLocalView.as_view(), name='search_local_page'),  # http://127.0.0.1:8000/local
]