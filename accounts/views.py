import hashlib
import hmac
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from applications.models import Application
from recommendations.engine import get_recommendations
from trips.models import Trip

from .forms import ProfileForm

User = get_user_model()


def profile_detail(request, pk):
    profile_user = get_object_or_404(User, pk=pk)
    profile = profile_user.profile
    trips = profile_user.organized_trips.all().order_by('-created_at')
    reviews = profile_user.reviews_received.select_related('author', 'trip').all()
    return render(request, 'accounts/profile_detail.html', {
        'profile_user': profile_user,
        'profile': profile,
        'trips': trips,
        'reviews': reviews,
    })


@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect('accounts:profile_detail', pk=request.user.pk)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def dashboard(request):
    my_trips = Trip.objects.filter(organizer=request.user).order_by('-created_at')
    my_applications = Application.objects.filter(user=request.user).select_related('trip').order_by('-created_at')
    applications_for_my_trips = Application.objects.filter(
        trip__organizer=request.user
    ).select_related('trip', 'user').order_by('-created_at')
    recommendations = get_recommendations(request.user, limit=5)

    return render(request, 'accounts/dashboard.html', {
        'my_trips': my_trips,
        'my_applications': my_applications,
        'applications_for_my_trips': applications_for_my_trips,
        'recommendations': recommendations,
    })


def _check_telegram_hash(data):
    """Проверка подлинности данных Telegram Login Widget.
    См. https://core.telegram.org/widgets/login#checking-authorization
    """
    received_hash = data.get('hash')
    if not received_hash or not settings.TELEGRAM_BOT_TOKEN:
        return False

    check_pairs = sorted(
        f'{k}={v}' for k, v in data.items() if k != 'hash'
    )
    data_check_string = '\n'.join(check_pairs)
    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return False

    auth_date = int(data.get('auth_date', 0))
    if time.time() - auth_date > 86400:  # ссылка авторизации старше суток — просрочена
        return False
    return True


def telegram_login(request):
    """Callback для Telegram Login Widget. Виджет присылает GET-параметры
    (id, first_name, username, photo_url, auth_date, hash), подписанные
    токеном бота — пароль Telegram при этом никогда не передаётся сайту."""
    data = request.GET.dict()

    if not settings.TELEGRAM_BOT_TOKEN:
        messages.error(request, 'Вход через Telegram временно недоступен: бот не настроен.')
        return redirect('account_login')

    if not data.get('id') or not _check_telegram_hash(data):
        messages.error(request, 'Не удалось подтвердить подлинность данных Telegram.')
        return redirect('account_login')

    telegram_id = data['id']
    username = data.get('username') or f'tg_{telegram_id}'

    user, created = User.objects.get_or_create(
        username=f'tg_{telegram_id}',
        defaults={'first_name': data.get('first_name', '')},
    )
    profile = user.profile
    if data.get('username') and not profile.telegram_url:
        profile.telegram_url = f'https://t.me/{data["username"]}'
        profile.save(update_fields=['telegram_url'])

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    messages.success(request, 'Вы вошли через Telegram.')
    return redirect(settings.LOGIN_REDIRECT_URL)


def max_login_stub(request):
    """Заглушка для входа через MAX: официального OAuth пока нет,
    архитектурно место подготовлено (см. settings.MAX_AUTH_ENABLED)."""
    return render(request, 'accounts/max_stub.html')
