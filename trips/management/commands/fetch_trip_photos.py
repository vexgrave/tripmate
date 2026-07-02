"""
Подбирает и скачивает реальные тематические фото для демонстрационных поездок
из Wikimedia Commons (свободно лицензированные изображения, API не требует ключа).

Использование: python manage.py fetch_trip_photos [--force]
"""
import time

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from trips.models import Trip, TripPhoto

API_URL = 'https://commons.wikimedia.org/w/api.php'
# API commons.wikimedia.org принимает описательный User-Agent, а вот CDN
# upload.wikimedia.org (где реально лежат файлы) отдаёт 403 на такие заголовки
# и требует браузероподобный User-Agent — поэтому для скачивания используем отдельный.
API_HEADERS = {'User-Agent': 'TripMateEduProject/1.0 (student project; contact: example@example.com)'}
DOWNLOAD_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/124.0 Safari/537.36',
}

BLACKLIST_WORDS = [
    'icon', 'logo', 'flag', 'map', 'diagram', 'seal', 'coat of arms', 'symbol',
    'chart', 'graph', 'screenshot', 'document', 'locator', 'emblem', 'svg',
]

# Название поездки -> поисковые запросы для обложки и галереи (на английском —
# так Wikimedia Commons даёт заметно более релевантную и качественную выдачу).
TRIP_PHOTO_QUERIES = {
    'Поход на Эльбрус (базовый лагерь)': {
        'cover': 'Mount Elbrus snow peak',
        'gallery': ['Caucasus mountains hiking trail', 'mountaineering camp tent snow'],
    },
    'Выходные в Суздале': {
        'cover': 'Suzdal Russia church golden domes',
        'gallery': ['Suzdal kremlin wooden architecture', 'Golden Ring Russia town'],
    },
    'Фестиваль электронной музыки': {
        'cover': 'music festival crowd night stage lights',
        'gallery': ['concert stage lights crowd', 'DJ festival crowd party'],
    },
    'Автопутешествие Казань — Москва': {
        'cover': 'highway road landscape',
        'gallery': ['road trip car', 'empty highway sunset landscape'],
    },
    'Экскурсия по Третьяковской галерее': {
        'cover': 'Tretyakov Gallery Moscow building facade',
        'gallery': ['art museum interior painting hall', 'museum gallery hall paintings'],
    },
    'Поход выходного дня в Карелию': {
        'cover': 'Karelia lake forest landscape',
        'gallery': ['Karelia nature rocks lake', 'forest lake Russia reflection'],
    },
    'Гастротур по Санкт-Петербургу': {
        'cover': 'Saint Petersburg street cafe',
        'gallery': ['street food market stall', 'restaurant table food dishes'],
    },
    'Фотопрогулка по вечерней Москве': {
        'cover': 'Moscow night city lights architecture',
        'gallery': ['Moscow Kremlin night illuminated', 'city street night lights long exposure'],
    },
    'Велопрогулка вдоль набережной': {
        'cover': 'cycling path riverside promenade',
        'gallery': ['bicycle path park trees', 'cyclists group road cycling'],
    },
    'Кемпинг на берегу озера': {
        'cover': 'camping tent lake shore',
        'gallery': ['campfire lake evening', 'tent lake forest'],
    },
    'Волонтёрская уборка леса': {
        'cover': 'forest cleanup volunteers trash bags',
        'gallery': ['volunteers nature trail cleanup', 'forest trail path green'],
    },
    'Джип-тур по Кавказу': {
        'cover': 'off-road jeep mountains dirt road',
        'gallery': ['Caucasus mountains road landscape', 'SUV mountain trail offroad'],
    },
    'Прошедший поход в Хибины': {
        'cover': 'Khibiny mountains',
        'gallery': ['arctic tundra mountains landscape', 'mountain hiking snow ridge'],
    },
}


class Command(BaseCommand):
    help = 'Скачивает тематические фото с Wikimedia Commons для демонстрационных поездок из seed_data.'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Перезаписать уже загруженные фото.')

    def handle(self, *args, **options):
        force = options['force']
        session = requests.Session()
        session.headers.update(API_HEADERS)

        for title, queries in TRIP_PHOTO_QUERIES.items():
            try:
                trip = Trip.objects.get(title=title)
            except Trip.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Пропуск: поездка "{title}" не найдена в базе.'))
                continue

            if not trip.image or force:
                image = self._find_and_download(session, queries['cover'])
                if image:
                    trip.image.save(image[0], ContentFile(image[1]), save=True)
                    self.stdout.write(self.style.SUCCESS(f'{title}: обложка сохранена ({queries["cover"]}).'))
                else:
                    self.stdout.write(self.style.WARNING(f'{title}: не удалось найти обложку.'))

            if force:
                trip.photos.all().delete()
            if trip.photos.count() == 0:
                for query in queries['gallery']:
                    image = self._find_and_download(session, query)
                    if image:
                        photo = TripPhoto(trip=trip)
                        photo.image.save(image[0], ContentFile(image[1]), save=True)
                        self.stdout.write(self.style.SUCCESS(f'{title}: фото галереи добавлено ({query}).'))
                    else:
                        self.stdout.write(self.style.WARNING(f'{title}: не удалось найти фото для "{query}".'))

        self.stdout.write(self.style.SUCCESS('Готово.'))

    def _find_and_download(self, session, query):
        """Ищет на Wikimedia Commons подходящее фото по запросу и возвращает
        (filename, bytes) первого удачного результата, либо None.
        Между скачиваниями выдерживается пауза и повтор при 429 — CDN
        upload.wikimedia.org достаточно быстро ограничивает частые запросы."""
        candidates = self._search(session, query)
        for title in candidates:
            info = self._get_image_info(session, title)
            if not info:
                continue
            if info['mime'] not in ('image/jpeg', 'image/png'):
                continue
            if info['width'] < 800 or info['height'] < 500:
                continue
            url = info.get('thumburl') or info['url']

            time.sleep(1.2)
            resp = self._download_with_retry(session, url)
            if resp is None:
                continue

            ext = 'png' if info['mime'] == 'image/png' else 'jpg'
            filename = f"{query.replace(' ', '_')[:40]}.{ext}"
            return filename, resp.content
        return None

    def _download_with_retry(self, session, url, retries=2):
        for attempt in range(retries + 1):
            try:
                resp = session.get(url, headers=DOWNLOAD_HEADERS, timeout=20)
            except requests.RequestException:
                return None
            if resp.status_code == 200:
                return resp
            if resp.status_code == 429 and attempt < retries:
                wait = float(resp.headers.get('Retry-After', 5))
                time.sleep(wait)
                continue
            return None
        return None

    def _search(self, session, query):
        params = {
            'action': 'query', 'list': 'search', 'srsearch': query,
            'srnamespace': 6, 'format': 'json', 'srlimit': 10,
        }
        try:
            resp = session.get(API_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError):
            return []

        titles = []
        for item in data.get('query', {}).get('search', []):
            title = item['title']
            lower = title.lower()
            if not lower.endswith(('.jpg', '.jpeg', '.png')):
                continue
            if any(word in lower for word in BLACKLIST_WORDS):
                continue
            titles.append(title)
        time.sleep(0.2)
        return titles

    def _get_image_info(self, session, title):
        params = {
            'action': 'query', 'titles': title, 'prop': 'imageinfo',
            'iiprop': 'url|mime|size', 'iiurlwidth': 1280, 'format': 'json',
        }
        try:
            resp = session.get(API_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError):
            return None

        pages = data.get('query', {}).get('pages', {})
        for page in pages.values():
            infos = page.get('imageinfo')
            if not infos:
                continue
            info = infos[0]
            return {
                'url': info.get('url'),
                'thumburl': info.get('thumburl'),
                'mime': info.get('mime'),
                'width': info.get('thumbwidth') or info.get('width', 0),
                'height': info.get('thumbheight') or info.get('height', 0),
            }
        return None
