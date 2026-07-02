from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from trips.models import Trip

from .forms import ApplicationForm
from .models import Application


@login_required
def application_create(request, trip_pk):
    trip = get_object_or_404(Trip, pk=trip_pk)

    if trip.organizer == request.user:
        messages.error(request, 'Нельзя подать заявку на собственную поездку.')
        return redirect('trips:trip_detail', pk=trip.pk)

    if Application.objects.filter(trip=trip, user=request.user).exists():
        messages.warning(request, 'Вы уже подавали заявку на эту поездку.')
        return redirect('trips:trip_detail', pk=trip.pk)

    if trip.status != Trip.Status.ACTIVE:
        messages.error(request, 'Эта поездка сейчас не принимает заявки.')
        return redirect('trips:trip_detail', pk=trip.pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.trip = trip
            application.user = request.user
            application.full_clean()
            application.save()
            messages.success(request, 'Заявка отправлена организатору.')
            return redirect('trips:trip_detail', pk=trip.pk)
    else:
        form = ApplicationForm()

    return render(request, 'applications/application_form.html', {'form': form, 'trip': trip})


@login_required
def application_accept(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if application.trip.organizer != request.user:
        raise PermissionDenied('Управлять заявками может только организатор поездки.')

    if request.method == 'POST':
        if application.trip.is_full:
            messages.error(request, 'В поездке уже нет свободных мест.')
        else:
            application.status = Application.Status.ACCEPTED
            application.save(update_fields=['status', 'updated_at'])
            messages.success(request, f'Заявка от {application.user.username} принята.')
    return redirect('trips:trip_detail', pk=application.trip.pk)


@login_required
def application_reject(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if application.trip.organizer != request.user:
        raise PermissionDenied('Управлять заявками может только организатор поездки.')

    if request.method == 'POST':
        application.status = Application.Status.REJECTED
        application.save(update_fields=['status', 'updated_at'])
        messages.info(request, f'Заявка от {application.user.username} отклонена.')
    return redirect('trips:trip_detail', pk=application.trip.pk)


@login_required
def application_cancel(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if application.user != request.user:
        raise PermissionDenied('Отменить можно только собственную заявку.')

    if request.method == 'POST':
        application.status = Application.Status.CANCELLED
        application.save(update_fields=['status', 'updated_at'])
        messages.info(request, 'Заявка отменена.')
    return redirect(request.POST.get('next') or 'accounts:dashboard')
