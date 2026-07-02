from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm
from django.contrib.auth.models import User

from .models import Interest, Profile


class UserChangeForm(DjangoUserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
            self.fields['password'].help_text = ''


class UserAdmin(DjangoUserAdmin):
    form = UserChangeForm


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


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
