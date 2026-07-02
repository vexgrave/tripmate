from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from applications.models import Application
from trips.models import Trip

from .forms import ReviewForm
from .models import Review

User = get_user_model()


def _is_participant(user, trip):
    if user == trip.organizer:
        return True
    return Application.objects.filter(trip=trip, user=user, status=Application.Status.ACCEPTED).exists()


@login_required
def review_create(request, trip_pk, user_pk):
    trip = get_object_or_404(Trip, pk=trip_pk)
    target_user = get_object_or_404(User, pk=user_pk)

    if target_user == request.user:
        raise PermissionDenied('Нельзя оставить отзыв самому себе.')

    if not _is_participant(request.user, trip) or not _is_participant(target_user, trip):
        raise PermissionDenied('Отзыв можно оставить только участнику совместной поездки.')

    if Review.objects.filter(trip=trip, author=request.user, target_user=target_user).exists():
        messages.warning(request, 'Вы уже оставляли отзыв этому пользователю по этой поездке.')
        return redirect('trips:trip_detail', pk=trip.pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.trip = trip
            review.author = request.user
            review.target_user = target_user
            review.full_clean()
            review.save()
            messages.success(request, f'Отзыв для {target_user.username} сохранён.')
            return redirect('trips:trip_detail', pk=trip.pk)
    else:
        form = ReviewForm()

    return render(request, 'reviews/review_form.html', {
        'form': form, 'trip': trip, 'target_user': target_user,
    })
