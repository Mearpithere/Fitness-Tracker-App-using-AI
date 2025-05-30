from django.db import models
from django.contrib.auth.models import AbstractUser
from djongo import models as djongo_models
from django.utils import timezone
import uuid

# Custom User model for OctoFit Tracker
class User(AbstractUser):
    email = models.EmailField(unique=True)
    grade_level = models.IntegerField(null=True, blank=True)
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    fitness_goals = models.JSONField(default=list, blank=True)
    preferred_activities = models.JSONField(default=list, blank=True)
    total_workouts = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    is_team_captain = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    # Fix reverse accessor conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='tracker_users',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='tracker_users',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return f"{self.username} ({self.email})"

# Team model
class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True)
    captain = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='captained_team')
    created_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    total_points = models.IntegerField(default=0)
    total_workouts = models.IntegerField(default=0)
    member_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'teams'
        ordering = ['-total_points', 'name']
    
    def __str__(self):
        return self.name
    
    def update_stats(self):
        """Update team statistics based on member activities"""
        members = self.user_set.all()
        self.member_count = members.count()
        self.total_points = sum(member.total_points for member in members)
        self.total_workouts = sum(member.total_workouts for member in members)
        self.save()

# Activity model
class Activity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50)
    points_per_minute = models.IntegerField(default=1)
    points_per_rep = models.IntegerField(default=0)
    description = models.TextField(max_length=300, blank=True)
    measurement_type = models.CharField(max_length=20, choices=[
        ('time', 'Time (minutes)'),
        ('distance', 'Distance'),
        ('reps', 'Repetitions'),
        ('sets', 'Sets')
    ], default='time')
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'activities'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.category})"

# Workout model
class Workout(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    duration_minutes = models.IntegerField(null=True, blank=True)
    distance = models.FloatField(null=True, blank=True)
    repetitions = models.IntegerField(null=True, blank=True)
    sets = models.IntegerField(null=True, blank=True)
    points_earned = models.IntegerField(default=0)
    date_logged = models.DateTimeField(default=timezone.now)
    notes = models.TextField(max_length=500, blank=True)
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_workouts')
    
    class Meta:
        db_table = 'workouts'
        ordering = ['-date_logged']
    
    def __str__(self):
        return f"{self.user.username} - {self.activity.name} ({self.date_logged.date()})"
    
    def calculate_points(self):
        """Calculate points based on activity and workout metrics"""
        if self.activity.measurement_type == 'time' and self.duration_minutes:
            self.points_earned = self.duration_minutes * self.activity.points_per_minute
        elif self.activity.measurement_type == 'reps' and self.repetitions:
            self.points_earned = self.repetitions * self.activity.points_per_rep
        else:
            self.points_earned = 0
        return self.points_earned
    
    def save(self, *args, **kwargs):
        if not self.points_earned:
            self.calculate_points()
        super().save(*args, **kwargs)

# Leaderboard model
class Leaderboard(models.Model):
    LEADERBOARD_TYPES = [
        ('individual', 'Individual'),
        ('team', 'Team'),
    ]
    
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('all_time', 'All Time'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20, choices=LEADERBOARD_TYPES)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    rankings = models.JSONField(default=list)
    last_updated = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'leaderboard'
        # unique_together = ['type', 'period', 'period_start']  # Temporarily disabled for djongo compatibility
        ordering = ['-period_start']
    
    def __str__(self):
        return f"{self.type.title()} {self.period.title()} Leaderboard ({self.period_start.date()})"
    
    def update_rankings(self):
        """Update leaderboard rankings based on current data"""
        if self.type == 'individual':
            users = User.objects.filter(
                workouts__date_logged__gte=self.period_start,
                workouts__date_logged__lte=self.period_end
            ).distinct()
            
            rankings = []
            for user in users:
                total_points = sum(
                    workout.points_earned for workout in user.workouts.filter(
                        date_logged__gte=self.period_start,
                        date_logged__lte=self.period_end
                    )
                )
                total_workouts = user.workouts.filter(
                    date_logged__gte=self.period_start,
                    date_logged__lte=self.period_end
                ).count()
                
                rankings.append({
                    'user_id': str(user.id),
                    'username': user.username,
                    'points': total_points,
                    'workouts': total_workouts
                })
            
            # Sort by points descending
            rankings.sort(key=lambda x: x['points'], reverse=True)
            
            # Add rank numbers
            for i, ranking in enumerate(rankings):
                ranking['rank'] = i + 1
            
            self.rankings = rankings
        
        elif self.type == 'team':
            teams = Team.objects.filter(is_active=True)
            rankings = []
            
            for team in teams:
                team_points = sum(
                    workout.points_earned for workout in Workout.objects.filter(
                        user__team=team,
                        date_logged__gte=self.period_start,
                        date_logged__lte=self.period_end
                    )
                )
                team_workouts = Workout.objects.filter(
                    user__team=team,
                    date_logged__gte=self.period_start,
                    date_logged__lte=self.period_end
                ).count()
                
                rankings.append({
                    'team_id': str(team.id),
                    'team_name': team.name,
                    'points': team_points,
                    'workouts': team_workouts,
                    'member_count': team.member_count
                })
            
            # Sort by points descending
            rankings.sort(key=lambda x: x['points'], reverse=True)
            
            # Add rank numbers
            for i, ranking in enumerate(rankings):
                ranking['rank'] = i + 1
            
            self.rankings = rankings
        
        self.last_updated = timezone.now()
        self.save()
