from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='graph_view'),
    path('csv_upload', views.csv_upload),
    path('graph', views.graph),
]