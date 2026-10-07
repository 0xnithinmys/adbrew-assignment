"""Root URL configuration. Each feature owns its routes in its own urls.py."""
from django.urls import include, path

urlpatterns = [
    path('todos/', include('todos.urls')),
]
