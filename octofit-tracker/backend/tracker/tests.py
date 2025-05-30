from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from .models import User, Team, Activity, Workout, Leaderboard

User = get_user_model()

# Create your tests here.

class UserModelTest(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@mergington.edu',
            password='testpass123',
            grade_level=10
        )
    
    def test_user_creation(self):
        """Test user creation with custom fields"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@mergington.edu')
        self.assertEqual(self.user.grade_level, 10)
        self.assertEqual(self.user.total_points, 0)
        self.assertEqual(self.user.total_workouts, 0)
    
    def test_user_str_method(self):
        """Test user string representation"""
        expected = f"{self.user.username} ({self.user.email})"
        self.assertEqual(str(self.user), expected)

class TeamModelTest(TestCase):
    """Test cases for Team model"""
    
    def setUp(self):
        self.captain = User.objects.create_user(
            username='captain',
            email='captain@mergington.edu',
            password='captainpass'
        )
        self.team = Team.objects.create(
            name='Thunder Hawks',
            description='Best team ever',
            captain=self.captain
        )
    
    def test_team_creation(self):
        """Test team creation"""
        self.assertEqual(self.team.name, 'Thunder Hawks')
        self.assertEqual(self.team.captain, self.captain)
        self.assertTrue(self.team.is_active)
        self.assertEqual(self.team.total_points, 0)
    
    def test_team_str_method(self):
        """Test team string representation"""
        self.assertEqual(str(self.team), 'Thunder Hawks')

class ActivityModelTest(TestCase):
    """Test cases for Activity model"""
    
    def setUp(self):
        self.activity = Activity.objects.create(
            name='Running',
            category='Cardio',
            points_per_minute=2,
            measurement_type='time'
        )
    
    def test_activity_creation(self):
        """Test activity creation"""
        self.assertEqual(self.activity.name, 'Running')
        self.assertEqual(self.activity.category, 'Cardio')
        self.assertEqual(self.activity.points_per_minute, 2)
        self.assertTrue(self.activity.is_active)
    
    def test_activity_str_method(self):
        """Test activity string representation"""
        expected = f"{self.activity.name} ({self.activity.category})"
        self.assertEqual(str(self.activity), expected)

class WorkoutModelTest(TestCase):
    """Test cases for Workout model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='athlete',
            email='athlete@mergington.edu',
            password='athletepass'
        )
        self.activity = Activity.objects.create(
            name='Cycling',
            category='Cardio',
            points_per_minute=3,
            measurement_type='time'
        )
        self.workout = Workout.objects.create(
            user=self.user,
            activity=self.activity,
            duration_minutes=30
        )
    
    def test_workout_creation(self):
        """Test workout creation"""
        self.assertEqual(self.workout.user, self.user)
        self.assertEqual(self.workout.activity, self.activity)
        self.assertEqual(self.workout.duration_minutes, 30)
        self.assertFalse(self.workout.verified)
    
    def test_points_calculation(self):
        """Test automatic points calculation"""
        expected_points = 30 * 3  # duration * points_per_minute
        self.assertEqual(self.workout.points_earned, expected_points)
    
    def test_workout_str_method(self):
        """Test workout string representation"""
        expected = f"{self.user.username} - {self.activity.name} ({self.workout.date_logged.date()})"
        self.assertEqual(str(self.workout), expected)

class LeaderboardModelTest(TestCase):
    """Test cases for Leaderboard model"""
    
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@mergington.edu',
            password='pass1'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@mergington.edu',
            password='pass2'
        )
        
        # Create activity
        self.activity = Activity.objects.create(
            name='Push-ups',
            category='Strength',
            points_per_rep=1,
            measurement_type='reps'
        )
        
        # Create workouts
        Workout.objects.create(
            user=self.user1,
            activity=self.activity,
            repetitions=50,
            verified=True
        )
        Workout.objects.create(
            user=self.user2,
            activity=self.activity,
            repetitions=30,
            verified=True
        )
        
        # Create leaderboard
        now = timezone.now()
        self.leaderboard = Leaderboard.objects.create(
            type='individual',
            period='weekly',
            period_start=now - timedelta(days=7),
            period_end=now
        )
    
    def test_leaderboard_creation(self):
        """Test leaderboard creation"""
        self.assertEqual(self.leaderboard.type, 'individual')
        self.assertEqual(self.leaderboard.period, 'weekly')
        self.assertEqual(len(self.leaderboard.rankings), 0)  # Empty until updated
    
    def test_leaderboard_str_method(self):
        """Test leaderboard string representation"""
        expected = f"{self.leaderboard.type.title()} {self.leaderboard.period.title()} Leaderboard ({self.leaderboard.period_start.date()})"
        self.assertEqual(str(self.leaderboard), expected)

class APITestCase(APITestCase):
    """Test cases for API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testapi',
            email='testapi@mergington.edu',
            password='apipass123'
        )
        self.activity = Activity.objects.create(
            name='Swimming',
            category='Cardio',
            points_per_minute=4
        )
    
    def test_api_root(self):
        """Test API root endpoint"""
        url = reverse('api-root')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('users', response.data)
        self.assertIn('teams', response.data)
        self.assertIn('activities', response.data)
        self.assertIn('workouts', response.data)
        self.assertIn('leaderboard', response.data)
    
    def test_users_list(self):
        """Test users list endpoint"""
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_activities_list(self):
        """Test activities list endpoint"""
        url = reverse('activity-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_workout_creation(self):
        """Test creating a workout via API"""
        url = reverse('workout-list')
        data = {
            'user': self.user.id,
            'activity': self.activity.id,
            'duration_minutes': 45,
            'notes': 'Great workout!'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Workout.objects.count(), 1)
        
        # Check points calculation
        workout = Workout.objects.first()
        expected_points = 45 * 4  # duration * points_per_minute
        self.assertEqual(workout.points_earned, expected_points)
