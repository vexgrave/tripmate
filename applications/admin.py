from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('trip', 'user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('trip__title', 'user__username')
    autocomplete_fields = ('trip', 'user')
    readonly_fields = ('created_at', 'updated_at')
