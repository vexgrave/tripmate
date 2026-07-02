"""
URL configuration for tripmate_project project.
"""
from allauth.account import views as allauth_views
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve as serve_static

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
# django.conf.urls.static.static() тут не подходит: она молча ничего не
# добавляет при DEBUG=False, поэтому маршрут прописан напрямую.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve_static, {'document_root': settings.MEDIA_ROOT}),
]
