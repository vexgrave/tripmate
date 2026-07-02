from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Аккаунты и профили'

    def ready(self):
        import accounts.signals  # noqa: F401

        # Django-переводы для admin строят фразы вроде "Добавить %(name)s" без
        # склонения — с verbose_name в именительном падеже получается
        # "Добавить пользователь". Ставим винительный падеж, чтобы фразы вида
        # "Добавить/Изменить пользователя" звучали грамотно.
        from django.contrib.auth.models import User
        User._meta.verbose_name = 'пользователя'
