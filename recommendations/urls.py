from django.urls import path

from . import views

app_name = 'recommendations'

urlpatterns = [
    path('', views.recommendations_list, name='recommendations_list'),
]
