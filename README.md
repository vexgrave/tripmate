# TripMate

Учебный веб-проект на Django: сайт для поиска попутчиков и компании для коротких поездок, прогулок, походов и мероприятий.

## Возможности

- Регистрация и вход по email (django-allauth), вход через VK, вход через Telegram (Login Widget), заглушка для MAX.
- Профиль пользователя: аватар, город, возраст, описание, интересы, рейтинг, ссылки на соцсети (Telegram/VK/Instagram/YouTube/другая).
- Создание, редактирование и удаление поездок (только автором), каталог с фильтрами и поиском.
- Заявки на участие: подача, принятие/отклонение организатором, отмена пользователем, защита от заявок на свою поездку и повторных заявок.
- Отзывы участников поездки друг о друге и автоматический пересчёт рейтинга профиля.
- Гибридная скоринговая система рекомендаций (`/recommendations/`) с объяснением, почему поездка подошла.
- Личный кабинет: свои поездки, свои заявки, заявки на свои поездки, рекомендации.
- Django Admin для всех моделей.

## Технологии

Python, Django 6, django-allauth (email + VK OAuth), SQLite, Bootstrap 5, Django Templates, Django Admin.

## Структура проекта

```
tripmate/
├── accounts/
│   ├── migrations/
│   ├── adapters.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
├── applications/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── core/
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── context_processors.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── recommendations/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── engine.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── reviews/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── trips/
│   ├── management/
│   │   └── commands/
│   │       └── fetch_trip_photos.py
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── static/
│   └── css/
│       └── style.css
├── templates/
│   ├── account/
│   ├── accounts/
│   ├── applications/
│   ├── core/
│   ├── recommendations/
│   ├── reviews/
│   ├── trips/
│   └── base.html
├── tripmate_project/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── .env.example
├── .gitignore
├── build.sh
├── manage.py
├── README.md
├── render.yaml
└── requirements.txt
```

## Запуск проекта локально

```bash
# 1. Создать виртуальное окружение
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Выполнить миграции
python manage.py migrate

# 4. Создать суперпользователя
python manage.py createsuperuser

# 5. (Необязательно, но рекомендуется) Заполнить базу тестовыми данными
python manage.py seed_data

# 6. Запустить сервер
python manage.py runserver

# 7. Открыть сайт в браузере
# http://127.0.0.1:8000/
```

Настройки для VK/Telegram/MAX и секретный ключ читаются из файла `.env` (см. `.env.example`). Без файла `.env` проект
запускается с безопасными значениями по умолчанию для локальной разработки — создавать `.env` для базового запуска
не обязательно.

## Тестовые данные

Команда `python manage.py seed_data` создаёт:

- 20 интересов (природа, фотография, походы, спорт, музыка, фестивали, музеи, архитектура, еда, путешествия,
  ночная жизнь, йога и медитация, кино, технологии, рыбалка, велоспорт, экстрим, настольные игры,
  ремёсла и творчество, волонтёрство);
- 8 пользователей с заполненными профилями и интересами (пароль для всех — `tripmate123`, email вида `anna@example.com`);
- 13 поездок разных категорий/транспорта (одна — со статусом «завершена» для демонстрации отзывов);
- ~20 заявок в разных статусах;
- ~15 отзывов с автоматическим пересчётом рейтинга организаторов.

Команда идемпотентна: повторный запуск не создаёт дублей (использует `get_or_create`).

Альтернатива — заполнить данные вручную через `/admin/` (доступна после `createsuperuser`).

## Вход через VK / Telegram / MAX

Функция подготовлена архитектурно, но требует ваших собственных ключей — секреты в проект не встроены:

- **VK**: получите `client_id`/`client_secret` VK-приложения (id.vk.com/business), впишите в `.env` как
  `VK_CLIENT_ID`/`VK_CLIENT_SECRET`. Redirect URI для приложения:
  `http://127.0.0.1:8000/accounts/3rdparty/vk/login/callback/`. Кнопка «Войти через VK» на странице `/login/` начнёт
  реально работать сразу после заполнения `.env`.
- **Telegram**: создайте бота через `@BotFather`, впишите токен и username бота в `.env`
  (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_BOT_USERNAME`). Виджет Telegram Login Widget требует HTTPS/публичный домен,
  привязанный к боту через `/setdomain` — для локальной разработки понадобится туннель (например, ngrok).
  Подлинность данных от Telegram проверяется на сервере по HMAC-подписи (`accounts/views.py::_check_telegram_hash`),
  пароль от Telegram при этом никогда не передаётся сайту.
- **MAX**: официального публичного OAuth/Login API нет, поэтому кнопка «Войти через MAX» ведёт на страницу-заглушку
  «Функция в разработке» (`/max/login/`). Архитектурно место подготовлено (`settings.MAX_AUTH_ENABLED`) и может быть
  включено, как только появится официальный способ авторизации.

## Система рекомендаций

`recommendations/engine.py` — гибридная скоринговая система на явных правилах. Для каждой активной поездки
считается `recommendation_score` как взвешенная сумма шести показателей:

```
recommendation_score =
    interest_score  * 0.40 +   # пересечение интересов пользователя и поездки (индекс Жаккара)
    city_score      * 0.15 +   # совпадает ли город пользователя с городом отправления
    budget_score    * 0.15 +   # насколько бюджет поездки близок к привычному для пользователя
    date_score      * 0.10 +   # насколько скоро состоится поездка
    rating_score    * 0.10 +   # рейтинг организатора (Profile.rating)
    popularity_score* 0.10     # просмотры и количество заявок относительно других активных поездок
```

Для каждой рекомендации формируется список коротких причин («совпадают интересы», «подходит город» и т.д.),
которые отображаются на странице `/recommendations/`, в блоке на главной и в личном кабинете.

## Безопасность

- Пароли хранятся стандартными средствами Django (хеширование).
- Все формы защищены CSRF-токенами.
- Редактировать/удалять поездку может только её организатор; управлять заявками — только организатор поездки;
  редактировать профиль — только его владелец (проверки на уровне views).
- Заявка на свою поездку и повторная заявка на одну поездку запрещены на уровне view и ограничения БД
  (`UniqueConstraint` в `applications.models.Application`).
- Пароли/токены социальных сетей нигде не запрашиваются и не хранятся — только публичные ссылки на профиль.
- Секретные ключи (`SECRET_KEY`, VK/Telegram credentials) читаются из `.env`, который исключён из git (`.gitignore`).

## Деплой на Render (бесплатный тариф)

Проект готов к деплою на [Render](https://render.com) как обычный Python/Django web service:

- `render.yaml` — Blueprint-описание сервиса (build/start команды, `SECRET_KEY` генерируется автоматически).
- `build.sh` — устанавливает зависимости, собирает статику (`collectstatic`, whitenoise) и применяет миграции.
- `whitenoise` — отдаёт статические файлы прямо из Django-процесса, отдельный веб-сервер для статики не нужен.
- `dj-database-url` — если к сервису подключить Render Postgres (переменная `DATABASE_URL` появится автоматически),
  проект переключится на неё сам; без неё используется SQLite.
