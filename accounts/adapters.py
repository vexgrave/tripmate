from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .models import Profile


class TripMateAccountAdapter(DefaultAccountAdapter):
    """Адаптер обычной регистрации по email.
    Редирект после регистрации на /profile/edit/ задаётся через
    settings.ACCOUNT_SIGNUP_REDIRECT_URL — здесь переопределять не нужно."""


class TripMateSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Заполняет Profile данными, которые вернул соцпровайдер (VK):
    имя, аватар, ссылка на страницу — без запроса пароля соцсети."""

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        if not user.username:
            base = data.get('email', '').split('@')[0] or f'user{sociallogin.account.uid}'
            user.username = base
        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        profile, _ = Profile.objects.get_or_create(user=user)

        extra = sociallogin.account.extra_data or {}
        provider = sociallogin.account.provider

        if provider == 'vk':
            # allauth VK provider кладёт в extra_data поля VK API (screen_name/domain и т.д.)
            screen_name = extra.get('domain') or extra.get('screen_name')
            if screen_name and not profile.vk_url:
                profile.vk_url = f'https://vk.com/{screen_name}'

        profile.save()
        return user
