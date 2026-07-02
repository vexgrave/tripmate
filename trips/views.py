from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from applications.models import Application
from reviews.models import Review

from .forms import TripCreateForm, TripFilterForm, TripForm
from .models import Trip, TripPhoto


def trip_list(request):
    trips = Trip.objects.filter(status=Trip.Status.ACTIVE).select_related('organizer', 'organizer__profile')
    form = TripFilterForm(request.GET or None)

    if form.is_valid():
        data = form.cleaned_data
        if data.get('q'):
            from django.db.models import Q
            trips = trips.filter(Q(title__icontains=data['q']) | Q(destination__icontains=data['q']))
        if data.get('departure_city'):
            trips = trips.filter(departure_city__icontains=data['departure_city'])
        if data.get('destination'):
            trips = trips.filter(destination__icontains=data['destination'])
        if data.get('date_from'):
            trips = trips.filter(date__gte=data['date_from'])
        if data.get('date_to'):
            trips = trips.filter(date__lte=data['date_to'])
        if data.get('budget_max') is not None:
            trips = trips.filter(budget__lte=data['budget_max'])
        if data.get('category'):
            trips = trips.filter(category=data['category'])
        if data.get('transport'):
            trips = trips.filter(transport=data['transport'])
        if data.get('interest'):
            trips = trips.filter(interests=data['interest'])

    trips = trips.distinct().order_by('-created_at')

    paginator = Paginator(trips, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'trips/trip_list.html', {
        'page_obj': page_obj,
        'form': form,
    })


def trip_detail(request, pk):
    trip = get_object_or_404(Trip.objects.select_related('organizer', 'organizer__profile'), pk=pk)

    if not request.user.is_authenticated or request.user != trip.organizer:
        Trip.objects.filter(pk=trip.pk).update(views_count=trip.views_count + 1)
        trip.views_count += 1

    my_application = None
    can_apply = False
    if request.user.is_authenticated:
        my_application = Application.objects.filter(trip=trip, user=request.user).first()
        can_apply = request.user != trip.organizer and my_application is None and trip.status == Trip.Status.ACTIVE

    applications = trip.applications.select_related('user', 'user__profile') if request.user == trip.organizer else None
    participants = trip.participants.select_related('profile')

    reviewed_user_ids = set()
    if request.user.is_authenticated:
        reviewed_user_ids = set(
            Review.objects.filter(trip=trip, author=request.user).values_list('target_user_id', flat=True)
        )

    return render(request, 'trips/trip_detail.html', {
        'trip': trip,
        'my_application': my_application,
        'can_apply': can_apply,
        'applications': applications,
        'participants': participants,
        'reviewed_user_ids': reviewed_user_ids,
        'gallery': trip.photos.all(),
    })


MAX_GALLERY_UPLOAD = 8


def _save_gallery_photos(request, trip):
    photos = request.FILES.getlist('photos')[:MAX_GALLERY_UPLOAD]
    TripPhoto.objects.bulk_create([TripPhoto(trip=trip, image=photo) for photo in photos])


@login_required
def trip_create(request):
    if request.method == 'POST':
        form = TripCreateForm(request.POST, request.FILES)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.organizer = request.user
            trip.save()
            form.save_m2m()
            _save_gallery_photos(request, trip)
            messages.success(request, 'Поездка создана.')
            return redirect('trips:trip_detail', pk=trip.pk)
    else:
        form = TripCreateForm()
    return render(request, 'trips/trip_form.html', {'form': form, 'is_create': True})


@login_required
def trip_edit(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    if trip.organizer != request.user:
        raise PermissionDenied('Редактировать поездку может только её организатор.')

    if request.method == 'POST':
        form = TripForm(request.POST, request.FILES, instance=trip)
        if form.is_valid():
            form.save()
            _save_gallery_photos(request, trip)
            messages.success(request, 'Поездка обновлена.')
            return redirect('trips:trip_detail', pk=trip.pk)
    else:
        form = TripForm(instance=trip)
    return render(request, 'trips/trip_form.html', {
        'form': form, 'is_create': False, 'trip': trip, 'gallery': trip.photos.all(),
    })


@login_required
def trip_photo_delete(request, pk, photo_pk):
    trip = get_object_or_404(Trip, pk=pk)
    if trip.organizer != request.user:
        raise PermissionDenied('Удалять фото может только организатор поездки.')

    photo = get_object_or_404(TripPhoto, pk=photo_pk, trip=trip)
    if request.method == 'POST':
        photo.delete()
        messages.success(request, 'Фото удалено.')
    return redirect('trips:trip_edit', pk=trip.pk)


@login_required
def trip_delete(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    if trip.organizer != request.user:
        raise PermissionDenied('Удалять поездку может только её организатор.')

    if request.method == 'POST':
        trip.delete()
        messages.success(request, 'Поездка удалена.')
        return redirect('trips:trip_list')
    return render(request, 'trips/trip_confirm_delete.html', {'trip': trip})
