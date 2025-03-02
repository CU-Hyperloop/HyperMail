# toolsapp/urls.py
# Sets up URL routing for the app. Defines how different URL patterns should be used by different views.

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.contrib.auth import views as auth_views

# Viewsets
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)), 
]