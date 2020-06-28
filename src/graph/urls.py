from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='graph_view'),
    path('graph', views.graph),
]