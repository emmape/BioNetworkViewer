from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('network/<str:n>/<str:f>/', views.network, name='viewNetwork'),
    path('download/', views.downloadNetwork, name='download'),
    path('downloadPng/', views.downloadNetworkAsPng, name='downloadPng'),

]
