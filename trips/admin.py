from django.contrib import admin

from .models import Trip, TripPhoto


class TripPhotoInline(admin.TabularInline):
    model = TripPhoto
    extra = 1


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'organizer', 'departure_city', 'destination', 'date',
        'category', 'transport', 'status', 'views_count', 'accepted_count',
    )
    list_filter = ('status', 'category', 'transport', 'date')
    search_fields = ('title', 'departure_city', 'destination', 'organizer__username')
    filter_horizontal = ('interests',)
    autocomplete_fields = ('organizer',)
    readonly_fields = ('views_count', 'created_at', 'updated_at')
    date_hierarchy = 'date'
    inlines = [TripPhotoInline]

    @admin.display(description='Принято')
    def accepted_count(self, obj):
        return obj.accepted_count
