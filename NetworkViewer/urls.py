from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('network/<str:n>/', views.network, name='viewNetwork'),
]
