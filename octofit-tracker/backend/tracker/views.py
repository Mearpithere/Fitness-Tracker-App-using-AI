
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from .models import User, Team, Activity, Workout, Leaderboard
from .serializers import (
    UserSerializer, TeamSerializer, ActivitySerializer, 
    WorkoutSerializer, LeaderboardSerializer
)

# Create your views here.

def index(request):
    """Welcome page for OctoFit Tracker API"""
    return JsonResponse({
        'message': 'Welcome to OctoFit Tracker API',
        'school': settings.OCTOFIT_SCHOOL_NAME,
        'version': '1.0.0'
    })

@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'service': 'OctoFit Tracker Backend',
        'school': settings.OCTOFIT_SCHOOL_NAME
    })

@api_view(['GET', 'POST'])
def api_root(request, format=None):
    """API root endpoint with links to all collections"""
    if request.method == 'POST':
        return Response({"message": "POST request received"}, status=status.HTTP_201_CREATED)

    # Use codespace URL for GitHub Codespaces environment
    codespace_url = 'https://potential-space-computing-machine-v9494vvw5773w9x9-8000.app.github.dev'
    
    # Check if running locally or in codespace
    if 'localhost' in request.get_host() or '127.0.0.1' in request.get_host():
        base_url = 'http://localhost:8000'
    else:
        base_url = codespace_url
    
    return Response({
        'users': f'{base_url}/api/users/?format=api',
        'teams': f'{base_url}/api/teams/?format=api', 
        'activities': f'{base_url}/api/activities/?format=api',
        'workouts': f'{base_url}/api/workouts/?format=api',
        'leaderboard': f'{base_url}/api/leaderboard/?format=api'
    })

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model with CRUD operations"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=True, methods=['get'])
    def workouts(self, request, pk=None):
        """Get all workouts for a specific user"""
        user = self.get_object()
        workouts = user.workouts.all()
        serializer = WorkoutSerializer(workouts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get user statistics"""
        user = self.get_object()
        return Response({
            'total_workouts': user.total_workouts,
            'total_points': user.total_points,
            'current_streak': user.current_streak,
            'longest_streak': user.longest_streak,
            'team': user.team.name if user.team else None,
            'rank': 'TBD'  # Can implement ranking logic
        })

class TeamViewSet(viewsets.ModelViewSet):
    """ViewSet for Team model with CRUD operations"""
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get all members of a team"""
        team = self.get_object()
        members = team.user_set.all()
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a team"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            user.team = team
            user.save()
            team.update_stats()
            return Response({'message': f'{user.username} joined {team.name}'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a team"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            if user.team == team:
                user.team = None
                user.save()
                team.update_stats()
                return Response({'message': f'{user.username} left {team.name}'})
            else:
                return Response({'error': 'User is not a member of this team'}, 
                              status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class ActivityViewSet(viewsets.ModelViewSet):
    """ViewSet for Activity model with CRUD operations"""
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all unique activity categories"""
        categories = Activity.objects.values_list('category', flat=True).distinct()
        return Response({'categories': list(categories)})

class WorkoutViewSet(viewsets.ModelViewSet):
    """ViewSet for Workout model with CRUD operations"""
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    
    def get_queryset(self):
        """Filter workouts by user if specified"""
        queryset = Workout.objects.all()
        user_id = self.request.query_params.get('user', None)
        if user_id is not None:
            queryset = queryset.filter(user=user_id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent workouts (last 7 days)"""
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_workouts = Workout.objects.filter(date_logged__gte=seven_days_ago)
        serializer = self.get_serializer(recent_workouts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a workout (admin/teacher only)"""
        workout = self.get_object()
        workout.verified = True
        workout.verified_by = request.user
        workout.save()
        
        # Update user stats
        user = workout.user
        user.total_workouts = user.workouts.filter(verified=True).count()
        user.total_points = sum(w.points_earned for w in user.workouts.filter(verified=True))
        user.save()
        
        return Response({'message': 'Workout verified'})

class LeaderboardViewSet(viewsets.ModelViewSet):
    """ViewSet for Leaderboard model with CRUD operations"""
    queryset = Leaderboard.objects.all()
    serializer_class = LeaderboardSerializer
    
    @action(detail=False, methods=['get'])
    def current_weekly(self, request):
        """Get current weekly individual leaderboard"""
        try:
            # Find or create current weekly leaderboard
            now = timezone.now()
            week_start = now - timedelta(days=now.weekday())
            week_end = week_start + timedelta(days=6)
            
            leaderboard, created = Leaderboard.objects.get_or_create(
                type='individual',
                period='weekly',
                period_start__date=week_start.date(),
                defaults={
                    'period_start': week_start,
                    'period_end': week_end
                }
            )
            
            # Update rankings
            leaderboard.update_rankings()
            serializer = self.get_serializer(leaderboard)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def current_monthly(self, request):
        """Get current monthly individual leaderboard"""
        try:
            now = timezone.now()
            month_start = now.replace(day=1)
            
            leaderboard, created = Leaderboard.objects.get_or_create(
                type='individual',
                period='monthly',
                period_start__date=month_start.date(),
                defaults={
                    'period_start': month_start,
                    'period_end': month_start.replace(month=month_start.month + 1) - timedelta(days=1)
                }
            )
            
            leaderboard.update_rankings()
            serializer = self.get_serializer(leaderboard)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def team_rankings(self, request):
        """Get current team leaderboard"""
        try:
            now = timezone.now()
            week_start = now - timedelta(days=now.weekday())
            week_end = week_start + timedelta(days=6)
            
            leaderboard, created = Leaderboard.objects.get_or_create(
                type='team',
                period='weekly',
                period_start__date=week_start.date(),
                defaults={
                    'period_start': week_start,
                    'period_end': week_end
                }
            )
            
            leaderboard.update_rankings()
            serializer = self.get_serializer(leaderboard)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
