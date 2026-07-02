from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from trips.models import Trip


class Review(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='reviews', verbose_name='Поездка')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reviews_written', verbose_name='Автор отзыва',
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reviews_received', verbose_name='Кому оставлен отзыв',
    )
    rating = models.PositiveSmallIntegerField(
        'Оценка', validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['trip', 'author', 'target_user'], name='unique_review_per_trip_pair',
            ),
        ]

    def __str__(self):
        return f'Отзыв {self.author} → {self.target_user} по поездке "{self.trip}" ({self.rating}/5)'

    def clean(self):
        if self.author_id and self.target_user_id and self.author_id == self.target_user_id:
            raise ValidationError('Нельзя оставить отзыв самому себе.')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.target_user.profile.recalculate_rating()

    def delete(self, *args, **kwargs):
        target = self.target_user
        super().delete(*args, **kwargs)
        target.profile.recalculate_rating()
