import random
from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Interest, Profile
from applications.models import Application
from reviews.models import Review
from trips.models import Trip

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
            result.append(trip)
        self.stdout.write(f'Поездки: {len(result)}')
        return result

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
