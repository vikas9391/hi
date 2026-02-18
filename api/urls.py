from django.urls import path
from . import views

urlpatterns = [
    path('gemini/', views.gemini_proxy, name='gemini'),  
]
