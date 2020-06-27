from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test_form', views.sample_form),
    path('csv_upload', views.csv_upload),
    path('graph', views.graph),
    path('session', views.view_session),
    path('clear', views.clear_session)
]