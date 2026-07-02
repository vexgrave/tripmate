from django.shortcuts import render

from trips.models import Trip


def home(request):
    latest_trips = Trip.objects.filter(status=Trip.Status.ACTIVE).select_related(
        'organizer', 'organizer__profile'
    ).order_by('-created_at')[:6]

    recommendations = []
    if request.user.is_authenticated:
        from recommendations.engine import get_recommendations
        recommendations = get_recommendations(request.user, limit=3)

    return render(request, 'core/home.html', {
        'latest_trips': latest_trips,
        'recommendations': recommendations,
    })
