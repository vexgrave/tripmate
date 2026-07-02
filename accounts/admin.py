from django.contrib import admin

from .models import Interest, Profile


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'age', 'rating', 'created_at')
    list_filter = ('city', 'interests')
    search_fields = ('user__username', 'user__email', 'city')
    filter_horizontal = ('interests',)
    autocomplete_fields = ('user',)
    readonly_fields = ('rating', 'created_at')
