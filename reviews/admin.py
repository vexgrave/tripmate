from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('trip', 'author', 'target_user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('trip__title', 'author__username', 'target_user__username')
    autocomplete_fields = ('trip', 'author', 'target_user')
    readonly_fields = ('created_at',)
