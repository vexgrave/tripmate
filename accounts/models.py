from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Interest(models.Model):
    """Интерес пользователя/поездки (природа, спорт, музыка и т.д.)."""

    name = models.CharField('Название', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Интерес'
        verbose_name_plural = 'Интересы'
        ordering = ['name']

    def __str__(self):
        return self.name


class Profile(models.Model):
    """Профиль пользователя, расширяющий стандартную модель User."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    city = models.CharField('Город', max_length=100, blank=True)
    age = models.PositiveSmallIntegerField('Возраст', blank=True, null=True)
    bio = models.TextField('О себе', blank=True)
    rating = models.DecimalField('Рейтинг', max_digits=3, decimal_places=2, default=0)
    interests = models.ManyToManyField(Interest, verbose_name='Интересы', blank=True, related_name='profiles')

    # социальные сети — только ссылки, без паролей
    telegram_url = models.URLField('Telegram', blank=True)
    vk_url = models.URLField('VK', blank=True)
    instagram_url = models.URLField('Instagram', blank=True)
    youtube_url = models.URLField('YouTube', blank=True)
    other_url = models.URLField('Другая ссылка', blank=True)

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль {self.user.username}'

    def get_absolute_url(self):
        return reverse('accounts:profile_detail', kwargs={'pk': self.user.pk})

    def recalculate_rating(self):
        """Пересчитывает средний рейтинг пользователя по отзывам, оставленным ему."""
        from reviews.models import Review

        agg = Review.objects.filter(target_user=self.user).aggregate(models.Avg('rating'))
        avg = agg['rating__avg']
        self.rating = round(avg, 2) if avg is not None else 0
        self.save(update_fields=['rating'])
