import random
from datetime import date, time, timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Interest, Profile
from applications.models import Application
from reviews.models import Review
from trips.models import Trip, TripPhoto

User = get_user_model()

INTERESTS = [
    'Природа', 'Фотография', 'Походы', 'Спорт', 'Музыка',
    'Фестивали', 'Музеи', 'Архитектура', 'Еда', 'Путешествия',
    'Ночная жизнь', 'Йога и медитация', 'Кино', 'Технологии', 'Рыбалка',
    'Велоспорт', 'Экстрим', 'Настольные игры', 'Ремёсла и творчество', 'Волонтёрство',
]

USERS = [
    dict(username='anna', email='anna@example.com', city='Москва', age=27, bio='Люблю горы и долгие пешие походы.', interests=['Природа', 'Походы', 'Фотография']),
    dict(username='ivan', email='ivan@example.com', city='Санкт-Петербург', age=31, bio='Организую поездки на выходные уже 5 лет.', interests=['Путешествия', 'Архитектура', 'Еда']),
    dict(username='maria', email='maria@example.com', city='Москва', age=24, bio='Фестивали, музыка и новые люди — моя стихия.', interests=['Музыка', 'Фестивали', 'Ночная жизнь']),
    dict(username='oleg', email='oleg@example.com', city='Казань', age=35, bio='За рулём с 2012 года, люблю дальние автопутешествия.', interests=['Путешествия', 'Спорт', 'Технологии']),
    dict(username='ekaterina', email='ekaterina@example.com', city='Москва', age=29, bio='Музеи и архитектура — обожаю городские экскурсии.', interests=['Музеи', 'Архитектура', 'Фотография']),
    dict(username='dmitry', email='dmitry@example.com', city='Нижний Новгород', age=26, bio='Ищу компанию для походов выходного дня.', interests=['Природа', 'Походы', 'Спорт', 'Велоспорт']),
    dict(username='polina', email='polina@example.com', city='Санкт-Петербург', age=22, bio='Люблю вкусно поесть и попробовать новую кухню в путешествиях.', interests=['Еда', 'Путешествия', 'Фотография']),
    dict(username='sergey', email='sergey@example.com', city='Екатеринбург', age=33, bio='Волонтёрю и катаюсь на велосипеде круглый год.', interests=['Волонтёрство', 'Велоспорт', 'Природа']),
]

TRIPS = [
    dict(organizer='anna', title='Поход на Эльбрус (базовый лагерь)', category=Trip.Category.HIKE, transport=Trip.Transport.BUS,
         departure_city='Москва', destination='Приэльбрусье', days_ahead=20, budget=15000, max_participants=6,
         interests=['Природа', 'Походы', 'Спорт'],
         description='Трёхдневный поход к подножию Эльбруса с ночёвкой в палатках. Опыт похода приветствуется.'),
    dict(organizer='ivan', title='Выходные в Суздале', category=Trip.Category.WEEKEND, transport=Trip.Transport.CAR,
         departure_city='Москва', destination='Суздаль', days_ahead=10, budget=6000, max_participants=4,
         interests=['Архитектура', 'Еда', 'Путешествия'],
         description='Едем на машине смотреть купола и есть медовуху. Ночуем в гостевом доме.'),
    dict(organizer='maria', title='Фестиваль электронной музыки', category=Trip.Category.EVENT, transport=Trip.Transport.TRAIN,
         departure_city='Москва', destination='Казань', days_ahead=35, budget=8000, max_participants=5,
         interests=['Музыка', 'Фестивали'],
         description='Едем большой компанией на open-air. Билеты у каждого свои, ищем попутчиков по дороге.'),
    dict(organizer='oleg', title='Автопутешествие Казань — Москва', category=Trip.Category.ROAD_TRIP, transport=Trip.Transport.CAR,
         departure_city='Казань', destination='Москва', days_ahead=5, budget=1500, max_participants=3,
         interests=['Путешествия', 'Технологии'],
         description='Еду по трассе М7, есть 3 свободных места. Можно с одним чемоданом.'),
    dict(organizer='ekaterina', title='Экскурсия по Третьяковской галерее', category=Trip.Category.EXCURSION, transport=Trip.Transport.WALK,
         departure_city='Москва', destination='Москва', days_ahead=7, budget=800, max_participants=8,
         interests=['Музеи', 'Архитектура'],
         description='Идём с экскурсоводом по основной экспозиции, затем кофе рядом.'),
    dict(organizer='dmitry', title='Поход выходного дня в Карелию', category=Trip.Category.HIKE, transport=Trip.Transport.TRAIN,
         departure_city='Санкт-Петербург', destination='Карелия', days_ahead=15, budget=5000, max_participants=6,
         interests=['Природа', 'Походы'],
         description='Озёра, скалы и лес. Берём палатки и котелок, готовим сами.'),
    dict(organizer='polina', title='Гастротур по Санкт-Петербургу', category=Trip.Category.FOOD_TOUR, transport=Trip.Transport.WALK,
         departure_city='Санкт-Петербург', destination='Санкт-Петербург', days_ahead=3, budget=2000, max_participants=5,
         interests=['Еда', 'Путешествия'],
         description='Обходим 5 лучших кафе центра города, дегустируем локальную кухню.'),
    dict(organizer='anna', title='Фотопрогулка по вечерней Москве', category=Trip.Category.PHOTO_TOUR, transport=Trip.Transport.WALK,
         departure_city='Москва', destination='Москва', days_ahead=2, budget=0, max_participants=10,
         interests=['Архитектура', 'Фотография'],
         description='Бесплатная прогулка по центру с фотоаппаратами, смотрим на подсветку зданий.'),
    dict(organizer='sergey', title='Велопрогулка вдоль набережной', category=Trip.Category.BIKE_RIDE, transport=Trip.Transport.OTHER,
         departure_city='Екатеринбург', destination='Екатеринбург', days_ahead=6, budget=0, max_participants=8,
         interests=['Велоспорт', 'Природа'],
         description='Едем не спеша, темп для всех уровней. Свой велосипед обязателен.'),
    dict(organizer='sergey', title='Кемпинг на берегу озера', category=Trip.Category.CAMPING, transport=Trip.Transport.CAR,
         departure_city='Екатеринбург', destination='озеро Тургояк', days_ahead=25, budget=4000, max_participants=6,
         interests=['Природа', 'Волонтёрство'],
         description='Два дня с палатками у воды: костёр, гитара, купание и уборка территории после отдыха.'),
    dict(organizer='dmitry', title='Волонтёрская уборка леса', category=Trip.Category.VOLUNTEERING, transport=Trip.Transport.BUS,
         departure_city='Нижний Новгород', destination='Ветлужский лес', days_ahead=12, budget=0, max_participants=15,
         interests=['Волонтёрство', 'Природа'],
         description='Экологическая акция: убираем мусор вдоль троп, обеспечиваем перчатками и мешками.'),
    dict(organizer='ivan', title='Джип-тур по Кавказу', category=Trip.Category.WEEKEND, transport=Trip.Transport.CAR,
         departure_city='Казань', destination='Домбай', days_ahead=45, budget=20000, max_participants=4,
         interests=['Природа', 'Путешествия', 'Спорт'],
         description='Едем на выходные на внедорожниках, нужен опыт горных дорог.'),
    dict(organizer='maria', title='Прошедший поход в Хибины', category=Trip.Category.HIKE, transport=Trip.Transport.TRAIN,
         departure_city='Санкт-Петербург', destination='Хибины', days_ahead=-10, budget=9000, max_participants=5,
         interests=['Природа', 'Походы', 'Спорт'], status=Trip.Status.COMPLETED,
         description='Уже прошедший поход — используется для демонстрации отзывов и рейтинга.'),
]

# Фото уже лежат в media/trips и media/trip_photos (см. trips/management/commands/fetch_trip_photos.py).
# Подключаем их по имени файла, чтобы не тянуть Wikimedia Commons заново при каждом деплое.
TRIP_PHOTOS = {
    'Поход на Эльбрус (базовый лагерь)': (
        'Mount_Elbrus_snow_peak_xFjYDHA.jpg',
        ['Caucasus_mountains_hiking_trail_3K1fR0f.jpg', 'mountaineering_camp_tent_snow_z0Fe3fI.jpg'],
    ),
    'Выходные в Суздале': (
        'Suzdal_Russia_church_golden_domes_q9KPHV3.jpg',
        ['Suzdal_kremlin_wooden_architecture_NAEsyl8.jpg', 'Golden_Ring_Russia_town_K5L8XDF.jpg'],
    ),
    'Фестиваль электронной музыки': (
        'music_festival_crowd_night_stage_lights_LQIE8YM.jpg',
        ['concert_stage_lights_crowd_20vyM48.jpg', 'DJ_festival_crowd_party_egC4lDD.jpg'],
    ),
    'Экскурсия по Третьяковской галерее': (
        'Tretyakov_Gallery_entrance_sign.jpg',
        ['art_museum_interior_painting_hall_H2IsRWN.jpg', 'museum_gallery_hall_paintings_QqvbdRB.jpg'],
    ),
    'Поход выходного дня в Карелию': (
        'Karelia_lake_forest_landscape_9k5lbeP.jpg',
        ['Karelia_nature_rocks_lake_p0BkaPx.jpg', 'forest_lake_Russia_reflection_tHPuXZS.jpg'],
    ),
    'Гастротур по Санкт-Петербургу': (
        'Saint_Petersburg_street_cafe_VulXiJe.jpg',
        ['street_food_market_stall_EaHif1m.jpg', 'restaurant_table_food_dishes_z9TlONw.jpg'],
    ),
    'Джип-тур по Кавказу': (
        'off-road_jeep_mountains_dirt_road_9Efe851.jpg',
        ['Caucasus_mountains_road_landscape_lW17x8N.jpg'],
    ),
    'Прошедший поход в Хибины': (
        'Khibiny_mountains.jpg',
        ['arctic_tundra_mountains_landscape_K2OiF28.jpg', 'mountain_hiking_snow_ridge_5eWoaIM.jpg'],
    ),
    'Автопутешествие Казань — Москва': ('highway_road_landscape.jpg', []),
    'Фотопрогулка по вечерней Москве': (
        'Moscow_night_city_lights_architecture_eCvzdGl.jpg',
        ['Moscow_Kremlin_night_illuminated_uU4stb0.jpg', 'city_street_night_lights_long_exposure_anUqyTs.jpg'],
    ),
    'Велопрогулка вдоль набережной': (
        'cycling_path_riverside_promenade_NFMbXjG.jpg',
        ['bicycle_path_park_trees_ygVCC3I.jpg'],
    ),
    'Кемпинг на берегу озера': (
        'camping_tent_lake_shore_PA73E8d.jpg',
        ['campfire_lake_evening.jpg', 'tent_lake_forest.jpg'],
    ),
    'Волонтёрская уборка леса': (
        'forest_cleanup_volunteers_trash_bags_cyyUgeN.jpg',
        ['volunteers_nature_trail_cleanup_L91AFoX.jpg', 'forest_trail_path_green_7PJ4Wqw.jpg'],
    ),
}


class Command(BaseCommand):
    help = 'Наполняет базу тестовыми данными: интересы, пользователи, поездки, заявки, отзывы.'

    @transaction.atomic
    def handle(self, *args, **options):
        interests = self._create_interests()
        users = self._create_users(interests)
        trips = self._create_trips(users, interests)
        self._create_applications(users, trips)
        self._create_reviews(users, trips)
        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы.'))

    def _create_interests(self):
        result = {}
        for name in INTERESTS:
            obj, _ = Interest.objects.get_or_create(name=name)
            result[name] = obj
        self.stdout.write(f'Интересы: {len(result)}')
        return result

    def _create_users(self, interests):
        result = {}
        for data in USERS:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={'email': data['email']},
            )
            if created:
                user.set_password('tripmate123')
                user.save()
            profile = user.profile
            profile.city = data['city']
            profile.age = data['age']
            profile.bio = data['bio']
            profile.save()
            profile.interests.set([interests[name] for name in data['interests']])
            result[data['username']] = user
        self.stdout.write(f'Пользователи: {len(result)} (пароль для всех: tripmate123)')
        return result

    def _create_trips(self, users, interests):
        result = []
        today = date.today()
        for data in TRIPS:
            trip, created = Trip.objects.get_or_create(
                title=data['title'],
                defaults=dict(
                    organizer=users[data['organizer']],
                    description=data['description'],
                    departure_city=data['departure_city'],
                    destination=data['destination'],
                    date=today + timedelta(days=data['days_ahead']),
                    time=time(10, 0),
                    budget=data['budget'],
                    max_participants=data['max_participants'],
                    category=data['category'],
                    transport=data['transport'],
                    status=data.get('status', Trip.Status.ACTIVE),
                    views_count=random.randint(5, 120),
                ),
            )
            if created:
                trip.interests.set([interests[name] for name in data['interests']])
            self._attach_photos(trip)
            result.append(trip)
        self.stdout.write(f'Поездки: {len(result)}')
        return result

    def _attach_photos(self, trip):
        """Подключает уже закоммиченные в media/ демо-фото к поездке по имени файла."""
        photos = TRIP_PHOTOS.get(trip.title)
        if not photos:
            return
        cover_name, gallery_names = photos

        if not trip.image:
            cover_path = Path(settings.MEDIA_ROOT) / 'trips' / cover_name
            if cover_path.exists():
                trip.image.name = f'trips/{cover_name}'
                trip.save(update_fields=['image'])

        if trip.photos.count() == 0:
            for name in gallery_names:
                photo_path = Path(settings.MEDIA_ROOT) / 'trip_photos' / name
                if photo_path.exists():
                    photo = TripPhoto(trip=trip)
                    photo.image.name = f'trip_photos/{name}'
                    photo.save()

    def _create_applications(self, users, trips):
        usernames = list(users.keys())
        count = 0
        for trip in trips:
            candidates = [u for name, u in users.items() if u != trip.organizer]
            random.shuffle(candidates)
            for applicant in candidates[:random.randint(1, 3)]:
                status = random.choice(
                    [Application.Status.PENDING, Application.Status.ACCEPTED, Application.Status.REJECTED]
                )
                _, created = Application.objects.get_or_create(
                    trip=trip, user=applicant,
                    defaults=dict(message='Хочу присоединиться!', status=status),
                )
                if created:
                    count += 1
        self.stdout.write(f'Заявки: {count}')

    def _create_reviews(self, users, trips):
        count = 0
        for trip in trips:
            accepted_users = list(
                User.objects.filter(applications__trip=trip, applications__status=Application.Status.ACCEPTED)
            )
            participants = accepted_users + [trip.organizer]
            if len(participants) < 2:
                continue
            for author in participants:
                for target in participants:
                    if author == target:
                        continue
                    if random.random() < 0.5:
                        continue
                    _, created = Review.objects.get_or_create(
                        trip=trip, author=author, target_user=target,
                        defaults=dict(
                            rating=random.randint(3, 5),
                            comment='Отличная компания, обязательно поедем ещё раз!',
                        ),
                    )
                    if created:
                        count += 1
        self.stdout.write(f'Отзывы: {count}')
