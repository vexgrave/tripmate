from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .engine import get_recommendations


@login_required
def recommendations_list(request):
    recommendations = get_recommendations(request.user, limit=10)
    return render(request, 'recommendations/recommendations_list.html', {
        'recommendations': recommendations,
    })
