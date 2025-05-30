from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Team, Activity, Workout, Leaderboard

# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin interface for custom User model"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'grade_level', 'team', 'total_points', 'is_team_captain')
    list_filter = ('grade_level', 'team', 'is_team_captain', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-total_points', 'username')
    
    fieldsets = UserAdmin.fieldsets + (
        ('OctoFit Profile', {
            'fields': ('grade_level', 'team', 'bio', 'fitness_goals', 'preferred_activities', 
                      'total_workouts', 'total_points', 'current_streak', 'longest_streak', 
                      'is_team_captain')
        }),
    )

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin interface for Team model"""
    list_display = ('name', 'captain', 'member_count', 'total_points', 'total_workouts', 'is_active', 'created_date')
    list_filter = ('is_active', 'created_date')
    search_fields = ('name', 'description')
    ordering = ('-total_points', 'name')
    readonly_fields = ('member_count', 'total_points', 'total_workouts')
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly for existing teams"""
        if obj:  # editing an existing object
            return self.readonly_fields + ('created_date',)
        return self.readonly_fields

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """Admin interface for Activity model"""
    list_display = ('name', 'category', 'measurement_type', 'points_per_minute', 'points_per_rep', 'is_active')
    list_filter = ('category', 'measurement_type', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('category', 'name')

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    """Admin interface for Workout model"""
    list_display = ('user', 'activity', 'duration_minutes', 'points_earned', 'date_logged', 'verified')
    list_filter = ('activity__category', 'verified', 'date_logged')
    search_fields = ('user__username', 'activity__name', 'notes')
    ordering = ('-date_logged',)
    readonly_fields = ('points_earned',)
    
    def get_queryset(self, request):
        """Optimize query to reduce database hits"""
        return super().get_queryset(request).select_related('user', 'activity', 'verified_by')

@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    """Admin interface for Leaderboard model"""
    list_display = ('type', 'period', 'period_start', 'period_end', 'last_updated')
    list_filter = ('type', 'period')
    ordering = ('-period_start',)
    readonly_fields = ('rankings', 'last_updated')
    
    actions = ['update_rankings']
    
    def update_rankings(self, request, queryset):
        """Admin action to update leaderboard rankings"""
        for leaderboard in queryset:
            leaderboard.update_rankings()
        self.message_user(request, f"{queryset.count()} leaderboards updated successfully.")
    update_rankings.short_description = "Update selected leaderboard rankings"
