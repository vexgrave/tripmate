"""
URL configuration for tripmate_project project.
"""
from allauth.account import views as allauth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    # Красивые адреса из ТЗ поверх allauth-вьюх
    path('register/', allauth_views.signup, name='register'),
    path('login/', allauth_views.login, name='login'),
    path('logout/', allauth_views.logout, name='logout'),

    # Полный набор allauth (сброс пароля, подтверждение email, OAuth VK и т.д.)
    path('accounts/', include('allauth.urls')),

    path('trips/', include('trips.urls')),
    path('applications/', include('applications.urls')),
    path('reviews/', include('reviews.urls')),
    path('recommendations/', include('recommendations.urls')),

    path('', include('accounts.urls')),
    path('', include('core.urls')),
]

# Медиафайлы (аватары, фото поездок) отдаются самим Django и в проде тоже —
# проект не использует отдельное файловое хранилище (S3 и т.п.).
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
