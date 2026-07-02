from django.conf import settings


def social_auth_settings(request):
    """Делает доступными в шаблонах настройки соцавторизации (Telegram/MAX)."""
    return {
        'TELEGRAM_BOT_USERNAME': settings.TELEGRAM_BOT_USERNAME,
        'MAX_AUTH_ENABLED': settings.MAX_AUTH_ENABLED,
    }
