from django.urls import path

from . import views

app_name = 'reviews'

urlpatterns = [
    path('trip/<int:trip_pk>/user/<int:user_pk>/review/', views.review_create, name='review_create'),
]
