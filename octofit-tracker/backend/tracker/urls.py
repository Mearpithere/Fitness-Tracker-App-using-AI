from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tracker import views
from .views import (
    UserViewSet, TeamViewSet, ActivityViewSet, 
    WorkoutViewSet, LeaderboardViewSet, api_root
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'activities', ActivityViewSet)
router.register(r'workouts', WorkoutViewSet)
router.register(r'leaderboard', LeaderboardViewSet)

app_name = 'tracker'

urlpatterns = [
    path('', views.index, name='index'),
    path('health/', views.health_check, name='health_check'),
    path('api-root/', api_root, name='api-root'),
    path('api/', include(router.urls)),
]
