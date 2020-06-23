from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test_form', views.sample_form),
    path('csv_upload', views.csv_upload)
]