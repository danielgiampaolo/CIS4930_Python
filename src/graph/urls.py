from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='graph_view'),
    path('download.csv', views.csv_download),
    path('graph', views.graph),
]