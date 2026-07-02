from django.urls import path

from . import views

app_name = 'applications'

urlpatterns = [
    path('trip/<int:trip_pk>/apply/', views.application_create, name='application_create'),
    path('<int:pk>/accept/', views.application_accept, name='application_accept'),
    path('<int:pk>/reject/', views.application_reject, name='application_reject'),
    path('<int:pk>/cancel/', views.application_cancel, name='application_cancel'),
]
