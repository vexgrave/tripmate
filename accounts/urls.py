from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/<int:pk>/', views.profile_detail, name='profile_detail'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('telegram/login/', views.telegram_login, name='telegram_login'),
    path('max/login/', views.max_login_stub, name='max_login_stub'),
]
