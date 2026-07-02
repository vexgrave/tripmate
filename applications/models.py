from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from trips.models import Trip


class Application(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'На рассмотрении'
        ACCEPTED = 'accepted', 'Принята'
        REJECTED = 'rejected', 'Отклонена'
        CANCELLED = 'cancelled', 'Отменена'

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='applications', verbose_name='Поездка')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='applications', verbose_name='Пользователь',
    )
    message = models.TextField('Сообщение', blank=True)
    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['trip', 'user'], name='unique_application_per_trip_user'),
        ]

    def __str__(self):
        return f'{self.user} → {self.trip} ({self.get_status_display()})'

    def clean(self):
        if self.trip_id and self.user_id and self.trip.organizer_id == self.user_id:
            raise ValidationError('Нельзя подать заявку на собственную поездку.')
