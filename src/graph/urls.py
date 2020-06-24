from django.urls import path

from . import views

urlpatterns = [
    path('old', views.index, name='index'),
    path('', views.node_list, name='list'),
]