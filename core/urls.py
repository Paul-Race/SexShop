from django.urls import path, include
from .views import client

urlpatterns = [
    #Cliente
    path("", client.index, name="index"),
    path('captcha/', include('captcha.urls')),
] 
