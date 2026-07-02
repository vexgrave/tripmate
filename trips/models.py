from django.conf import settings
from django.db import models
from django.urls import reverse

from accounts.models import Interest


class Trip(models.Model):
    class Category(models.TextChoices):
        WALK = 'walk', 'Прогулка'
        WEEKEND = 'weekend', 'Поездка на выходные'
        HIKE = 'hike', 'Поход'
        EVENT = 'event', 'Мероприятие'
        EXCURSION = 'excursion', 'Экскурсия'
        BIKE_RIDE = 'bike_ride', 'Велопрогулка'
        CAMPING = 'camping', 'Кемпинг'
        FOOD_TOUR = 'food_tour', 'Гастротур'
        PHOTO_TOUR = 'photo_tour', 'Фототур'
        ROAD_TRIP = 'road_trip', 'Автопутешествие'
        VOLUNTEERING = 'volunteering', 'Волонтёрство'
        OTHER = 'other', 'Другое'

    class Transport(models.TextChoices):
        WALK = 'walk', 'Пешком'
        CAR = 'car', 'Автомобиль'
        TRAIN = 'train', 'Поезд'
        BUS = 'bus', 'Автобус'
        SUBURBAN = 'suburban', 'Электричка'
        PLANE = 'plane', 'Самолёт'
        OTHER = 'other', 'Другое'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активна'
        COMPLETED = 'completed', 'Завершена'
        CANCELLED = 'cancelled', 'Отменена'
        ARCHIVED = 'archived', 'В архиве'

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='organized_trips', verbose_name='Организатор',
    )
    title = models.CharField('Название', max_length=150)
    description = models.TextField('Описание')
    image = models.ImageField('Изображение', upload_to='trips/', blank=True, null=True)

    departure_city = models.CharField('Город отправления', max_length=100)
    destination = models.CharField('Пункт назначения', max_length=100)
    date = models.DateField('Дата')
    time = models.TimeField('Время', blank=True, null=True)
    budget = models.PositiveIntegerField('Бюджет, ₽', default=0, help_text='0 — бесплатно')
    max_participants = models.PositiveSmallIntegerField('Максимум участников', default=4)

    category = models.CharField('Категория', max_length=20, choices=Category.choices, default=Category.OTHER)
    transport = models.CharField('Транспорт', max_length=20, choices=Transport.choices, default=Transport.OTHER)
    requirements = models.TextField('Требования к участникам', blank=True)
    interests = models.ManyToManyField(Interest, verbose_name='Интересы поездки', blank=True, related_name='trips')

    status = models.CharField('Статус', max_length=20, choices=Status.choices, default=Status.ACTIVE)
    views_count = models.PositiveIntegerField('Просмотры', default=0)

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Поездка'
        verbose_name_plural = 'Поездки'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('trips:trip_detail', kwargs={'pk': self.pk})

    @property
    def participants(self):
        """Пользователи с принятой заявкой на эту поездку."""
        from django.contrib.auth import get_user_model
        return get_user_model().objects.filter(
            applications__trip=self, applications__status='accepted'
        )

    @property
    def accepted_count(self):
        return self.applications.filter(status='accepted').count()

    @property
    def free_places(self):
        return max(self.max_participants - self.accepted_count, 0)

    @property
    def is_full(self):
        return self.free_places <= 0


class TripPhoto(models.Model):
    """Дополнительное фото направления/поездки (галерея на странице поездки)."""

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='photos', verbose_name='Поездка')
    image = models.ImageField('Фото', upload_to='trip_photos/')
    uploaded_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Фото поездки'
        verbose_name_plural = 'Фото поездки'
        ordering = ['uploaded_at']

    def __str__(self):
        return f'Фото для «{self.trip.title}»'
