"""
Гибридная система рекомендаций TripMate.

Для каждой активной поездки рассчитывается recommendation_score — взвешенная
сумма шести показателей (интересы, город, бюджет, дата, рейтинг организатора,
популярность). Формула и веса заданы техническим заданием проекта.

Это прозрачная скоринговая (rule-based) система: каждый показатель —
число от 0 до 1, вес показывает, насколько он важен относительно других.
Такой подход достаточен для MVP и легко объясним пользователю
("почему мне это порекомендовали").
"""
from datetime import date

from django.db.models import Count, Q

from trips.models import Trip

WEIGHTS = {
    'interest': 0.40,
    'city': 0.15,
    'budget': 0.15,
    'date': 0.10,
    'rating': 0.10,
    'popularity': 0.10,
}


def _interest_score(profile, trip):
    user_interests = set(profile.interests.values_list('id', flat=True))
    trip_interests = set(trip.interests.values_list('id', flat=True))
    if not user_interests or not trip_interests:
        return 0.3  # нейтральный балл, когда сравнивать нечего
    intersection = user_interests & trip_interests
    union = user_interests | trip_interests
    return len(intersection) / len(union)


def _city_score(profile, trip):
    if not profile.city or not trip.departure_city:
        return 0.3
    return 1.0 if profile.city.strip().lower() == trip.departure_city.strip().lower() else 0.0


def _budget_score(profile, trip, user_avg_budget):
    if user_avg_budget is None:
        # нет истории поездок — считаем, что более бюджетные варианты подходят чуть лучше
        return max(0.0, 1 - min(trip.budget, 15000) / 15000)
    diff = abs(trip.budget - user_avg_budget)
    scale = max(user_avg_budget, 1000)
    return max(0.0, 1 - diff / scale)


def _date_score(trip):
    days_until = (trip.date - date.today()).days
    if days_until < 0:
        return 0.0
    if days_until <= 7:
        return 1.0
    if days_until <= 30:
        return 0.7
    if days_until <= 90:
        return 0.4
    return 0.2


def _rating_score(organizer_profile):
    rating = float(organizer_profile.rating or 0)
    if rating <= 0:
        return 0.5  # нейтральный балл для новых организаторов без отзывов
    return min(rating / 5, 1.0)


def _popularity_score(trip, max_views, max_applications):
    views_part = (trip.views_count / max_views) if max_views else 0
    apps_part = (trip.applications.count() / max_applications) if max_applications else 0
    return round(0.4 * views_part + 0.6 * apps_part, 4)


def _explain(interest, city, budget, date_s, rating, popularity):
    reasons = []
    if interest >= 0.5:
        reasons.append('совпадают интересы')
    if city == 1.0:
        reasons.append('подходит город отправления')
    if budget >= 0.7:
        reasons.append('бюджет вам подходит')
    if date_s >= 0.7:
        reasons.append('поездка уже скоро')
    if rating >= 0.8:
        reasons.append('высокий рейтинг организатора')
    if popularity >= 0.6:
        reasons.append('популярная поездка')
    if not reasons:
        reasons.append('может быть интересно по общим параметрам')
    return reasons


def get_recommendations(user, limit=10):
    """Возвращает список словарей {trip, score, reasons, breakdown} —
    активные поездки, отсортированные по recommendation_score убыванию."""
    profile = user.profile

    trips = (
        Trip.objects.filter(status=Trip.Status.ACTIVE)
        .exclude(organizer=user)
        .exclude(applications__user=user)
        .select_related('organizer', 'organizer__profile')
        .prefetch_related('interests')
        .annotate(applications_count=Count('applications'))
        .distinct()
    )
    if not trips:
        return []

    max_views = max((t.views_count for t in trips), default=0)
    max_applications = max((t.applications_count for t in trips), default=0)

    history_budgets = list(
        Trip.objects.filter(
            Q(organizer=user) | Q(applications__user=user, applications__status='accepted')
        ).values_list('budget', flat=True)
    )
    user_avg_budget = sum(history_budgets) / len(history_budgets) if history_budgets else None

    results = []
    for trip in trips:
        interest = _interest_score(profile, trip)
        city = _city_score(profile, trip)
        budget = _budget_score(profile, trip, user_avg_budget)
        date_s = _date_score(trip)
        rating = _rating_score(trip.organizer.profile)
        popularity = _popularity_score(trip, max_views, max_applications)

        score = (
            interest * WEIGHTS['interest']
            + city * WEIGHTS['city']
            + budget * WEIGHTS['budget']
            + date_s * WEIGHTS['date']
            + rating * WEIGHTS['rating']
            + popularity * WEIGHTS['popularity']
        )

        results.append({
            'trip': trip,
            'score': round(score * 100, 1),  # в процентах для удобства отображения
            'reasons': _explain(interest, city, budget, date_s, rating, popularity),
            'breakdown': {
                'interest': round(interest, 2),
                'city': round(city, 2),
                'budget': round(budget, 2),
                'date': round(date_s, 2),
                'rating': round(rating, 2),
                'popularity': round(popularity, 2),
            },
        })

    results.sort(key=lambda r: r['score'], reverse=True)
    return results[:limit]
