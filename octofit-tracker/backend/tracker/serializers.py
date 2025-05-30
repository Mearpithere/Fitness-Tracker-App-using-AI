
from rest_framework import serializers
from .models import User, Team, Activity, Workout, Leaderboard
from bson import ObjectId
from django.contrib.auth.hashers import make_password

class ObjectIdField(serializers.Field):
    """Custom serializer field for MongoDB ObjectId"""
    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        try:
            return ObjectId(data)
        except:
            raise serializers.ValidationError("Invalid ObjectId format")

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    password = serializers.CharField(write_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'grade_level', 'team', 'team_name', 'bio', 'fitness_goals',
            'preferred_activities', 'total_workouts', 'total_points',
            'current_streak', 'longest_streak', 'is_team_captain',
            'date_joined', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        """Create a new user with hashed password"""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """Update user, handling password hashing if provided"""
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class UserSummarySerializer(serializers.ModelSerializer):
    """Lightweight user serializer for team member lists"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'total_points']

class TeamSerializer(serializers.ModelSerializer):
    """Serializer for Team model"""
    captain_name = serializers.CharField(source='captain.username', read_only=True)
    members = UserSummarySerializer(source='user_set', many=True, read_only=True)
    
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description', 'captain', 'captain_name',
            'created_date', 'is_active', 'total_points', 'total_workouts',
            'member_count', 'members'
        ]
    
    def validate_name(self, value):
        """Ensure team name is unique"""
        instance = getattr(self, 'instance', None)
        if Team.objects.filter(name=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("A team with this name already exists.")
        return value

class ActivitySerializer(serializers.ModelSerializer):
    """Serializer for Activity model"""
    
    class Meta:
        model = Activity
        fields = [
            'id', 'name', 'category', 'points_per_minute', 'points_per_rep',
            'description', 'measurement_type', 'is_active', 'created_date'
        ]

class WorkoutSerializer(serializers.ModelSerializer):
    """Serializer for Workout model"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    activity_name = serializers.CharField(source='activity.name', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.username', read_only=True)
    
    class Meta:
        model = Workout
        fields = [
            'id', 'user', 'user_name', 'activity', 'activity_name',
            'duration_minutes', 'distance', 'repetitions', 'sets',
            'points_earned', 'date_logged', 'notes', 'verified',
            'verified_by', 'verified_by_name'
        ]
        read_only_fields = ['points_earned', 'date_logged']

class LeaderboardSerializer(serializers.ModelSerializer):
    """Serializer for Leaderboard model"""
    
    class Meta:
        model = Leaderboard
        fields = [
            'id', 'type', 'period', 'period_start', 'period_end',
            'rankings', 'last_updated'
        ]
        read_only_fields = ['rankings', 'last_updated']

# Remove the ActivityTypeSerializer since ActivityType doesn't exist
