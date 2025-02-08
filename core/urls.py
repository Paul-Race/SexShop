from django.urls import path
from .views import client

urlpatterns = [
    #Cliente
    path("", client.index, name="index"),
]