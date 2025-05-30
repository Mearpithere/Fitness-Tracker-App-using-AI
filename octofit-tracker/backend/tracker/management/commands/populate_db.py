
from django.core.management.base import BaseCommand
from tracker.models import User, Team, Activity, Workout, Leaderboard
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid

class Command(BaseCommand):
    help = 'Populate the OctoFit database with test data for users, teams, activities, workouts, and leaderboards'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Clearing existing data...'))
        
        # Clear existing data
        Workout.objects.all().delete()
        Leaderboard.objects.all().delete()
        Activity.objects.all().delete()
        Team.objects.all().delete()
        User.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Creating test users...'))
        
        # Create users with superhero-themed names for Mergington High School
        users_data = [
            {
                'username': 'thundergod',
                'email': 'thundergod@mergington.edu',
                'first_name': 'Thor',
                'last_name': 'Odinson',
                'grade_level': 11,
                'bio': 'God of Thunder, loves hammer throws and lightning-fast workouts'
            },
            {
                'username': 'metalgeek',
                'email': 'metalgeek@mergington.edu', 
                'first_name': 'Tony',
                'last_name': 'Stark',
                'grade_level': 12,
                'bio': 'Genius inventor who builds custom workout equipment'
            },
            {
                'username': 'zerocool',
                'email': 'zerocool@mergington.edu',
                'first_name': 'Dade',
                'last_name': 'Murphy',
                'grade_level': 10,
                'bio': 'Elite hacker who optimizes workout algorithms'
            },
            {
                'username': 'crashoverride',
                'email': 'crashoverride@mergington.edu',
                'first_name': 'Kate',
                'last_name': 'Libby',
                'grade_level': 11,
                'bio': 'Cybersecurity expert with unstoppable determination'
            },
            {
                'username': 'sleeptoken',
                'email': 'sleeptoken@mergington.edu',
                'first_name': 'Vessel',
                'last_name': 'Anonymous',
                'grade_level': 12,
                'bio': 'Mysterious athlete who trains in the shadows'
            },
        ]
        
        users = []
        for user_data in users_data:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password='mergington123',  # Default password for testing
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                grade_level=user_data['grade_level'],
                bio=user_data['bio'],
                fitness_goals=['Build strength', 'Improve endurance', 'Team collaboration'],
                preferred_activities=['Running', 'Strength training', 'Team sports']
            )
            users.append(user)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))

        # Create teams
        self.stdout.write(self.style.SUCCESS('Creating teams...'))
        
        blue_team = Team.objects.create(
            name='Thunder Hawks',
            description='Lightning-fast athletes who soar above the competition',
            captain=users[0],  # thundergod as captain
            is_active=True
        )
        
        gold_team = Team.objects.create(
            name='Cyber Wolves',
            description='Tech-savvy athletes who hack their way to victory',
            captain=users[2],  # zerocool as captain
            is_active=True
        )
        
        # Assign users to teams
        users[0].team = blue_team
        users[0].is_team_captain = True
        users[1].team = blue_team
        users[2].team = gold_team
        users[2].is_team_captain = True
        users[3].team = gold_team
        users[4].team = gold_team
        
        for user in users:
            user.save()
        
        # Update team stats
        # blue_team.update_stats()
        # gold_team.update_stats()
        
        # Manually update team stats to avoid djongo issues
        blue_team.member_count = User.objects.filter(team=blue_team).count()
        blue_team.save()
        gold_team.member_count = User.objects.filter(team=gold_team).count()
        gold_team.save()
        
        self.stdout.write(self.style.SUCCESS('Created 2 teams and assigned members'))

        # Create activities
        self.stdout.write(self.style.SUCCESS('Creating fitness activities...'))
        
        activities_data = [
            {
                'name': 'Running',
                'category': 'Cardio',
                'points_per_minute': 2,
                'description': 'Outdoor or treadmill running for cardiovascular fitness',
                'measurement_type': 'time'
            },
            {
                'name': 'Cycling',
                'category': 'Cardio', 
                'points_per_minute': 3,
                'description': 'Stationary or road cycling for endurance',
                'measurement_type': 'time'
            },
            {
                'name': 'Push-ups',
                'category': 'Strength',
                'points_per_rep': 1,
                'description': 'Upper body strength exercise',
                'measurement_type': 'reps'
            },
            {
                'name': 'Swimming',
                'category': 'Cardio',
                'points_per_minute': 4,
                'description': 'Pool swimming for full-body cardio workout',
                'measurement_type': 'time'
            },
            {
                'name': 'Weight Training',
                'category': 'Strength',
                'points_per_minute': 3,
                'description': 'Free weights and machine exercises for strength building',
                'measurement_type': 'time'
            },
            {
                'name': 'Yoga',
                'category': 'Flexibility',
                'points_per_minute': 2,
                'description': 'Flexibility and mindfulness practice',
                'measurement_type': 'time'
            },
            {
                'name': 'Basketball',
                'category': 'Sports',
                'points_per_minute': 5,
                'description': 'Team sport for agility and coordination',
                'measurement_type': 'time'
            },
        ]
        
        activities = []
        for activity_data in activities_data:
            activity = Activity.objects.create(**activity_data)
            activities.append(activity)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(activities)} activities'))

        # Create workouts
        self.stdout.write(self.style.SUCCESS('Creating workout records...'))
        
        workouts_data = [
            # thundergod workouts
            {'user': users[0], 'activity': activities[0], 'duration_minutes': 30, 'notes': 'Morning run around campus'},
            {'user': users[0], 'activity': activities[4], 'duration_minutes': 45, 'notes': 'Heavy deadlifts and squats'},
            {'user': users[0], 'activity': activities[6], 'duration_minutes': 60, 'notes': 'Basketball practice with team'},
            
            # metalgeek workouts  
            {'user': users[1], 'activity': activities[1], 'duration_minutes': 45, 'notes': 'Built a custom bike computer'},
            {'user': users[1], 'activity': activities[4], 'duration_minutes': 40, 'notes': 'Testing new workout equipment'},
            {'user': users[1], 'activity': activities[2], 'repetitions': 50, 'notes': 'Modified push-up form for efficiency'},
            
            # zerocool workouts
            {'user': users[2], 'activity': activities[0], 'duration_minutes': 25, 'notes': 'Quick interval training'},
            {'user': users[2], 'activity': activities[3], 'duration_minutes': 30, 'notes': 'Swimming laps for cardio'},
            {'user': users[2], 'activity': activities[5], 'duration_minutes': 35, 'notes': 'Yoga for mental clarity'},
            
            # crashoverride workouts
            {'user': users[3], 'activity': activities[0], 'duration_minutes': 35, 'notes': 'Distance running training'},
            {'user': users[3], 'activity': activities[2], 'repetitions': 75, 'notes': 'Push-up challenge completed'},
            {'user': users[3], 'activity': activities[6], 'duration_minutes': 50, 'notes': 'Basketball scrimmage'},
            
            # sleeptoken workouts
            {'user': users[4], 'activity': activities[3], 'duration_minutes': 40, 'notes': 'Silent swimming session'},
            {'user': users[4], 'activity': activities[4], 'duration_minutes': 50, 'notes': 'Late night strength training'},
            {'user': users[4], 'activity': activities[5], 'duration_minutes': 30, 'notes': 'Meditation and stretching'},
        ]
        
        workouts = []
        for workout_data in workouts_data:
            workout = Workout.objects.create(**workout_data)
            workouts.append(workout)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(workouts)} workout records'))

        # Update user totals based on workouts
        for user in users:
            user_workouts = Workout.objects.filter(user=user)
            user.total_workouts = user_workouts.count()
            user.total_points = sum(workout.points_earned for workout in user_workouts)
            user.save()

        # Update team stats again
        # blue_team.update_stats()
        # gold_team.update_stats()
        
        # Manually calculate team points to avoid djongo issues
        blue_team_points = sum(User.objects.filter(team=blue_team).values_list('total_points', flat=True))
        blue_team.total_points = blue_team_points
        blue_team.save()
        
        gold_team_points = sum(User.objects.filter(team=gold_team).values_list('total_points', flat=True))
        gold_team.total_points = gold_team_points
        gold_team.save()

        # Create leaderboards
        self.stdout.write(self.style.SUCCESS('Creating leaderboards...'))
        
        now = timezone.now()
        
        # Weekly individual leaderboard
        weekly_leaderboard = Leaderboard.objects.create(
            type='individual',
            period='weekly',
            period_start=now - timedelta(days=7),
            period_end=now
        )
        # Skip automatic ranking update due to djongo compatibility issues
        # weekly_leaderboard.update_rankings()
        
        # Monthly team leaderboard
        monthly_team_leaderboard = Leaderboard.objects.create(
            type='team', 
            period='monthly',
            period_start=now - timedelta(days=30),
            period_end=now
        )
        # Skip automatic ranking update due to djongo compatibility issues
        # monthly_team_leaderboard.update_rankings()
        
        self.stdout.write(self.style.SUCCESS('Created leaderboards (rankings will be calculated separately)'))

        # Print summary
        self.stdout.write(self.style.SUCCESS('=== DATABASE POPULATION COMPLETE ==='))
        self.stdout.write(f'Users created: {User.objects.count()}')
        self.stdout.write(f'Teams created: {Team.objects.count()}')
        self.stdout.write(f'Activities created: {Activity.objects.count()}')
        self.stdout.write(f'Workouts created: {Workout.objects.count()}')
        self.stdout.write(f'Leaderboards created: {Leaderboard.objects.count()}')
        
        # Show team standings
        self.stdout.write(self.style.WARNING('\n=== TEAM STANDINGS ==='))
        for team in Team.objects.all().order_by('-total_points'):
            self.stdout.write(f'{team.name}: {team.total_points} points, {team.member_count} members')
        
        # Show top users
        self.stdout.write(self.style.WARNING('\n=== TOP USERS ==='))
        for user in User.objects.all().order_by('-total_points')[:3]:
            self.stdout.write(f'{user.username} ({user.first_name} {user.last_name}): {user.total_points} points')
        
        self.stdout.write(self.style.SUCCESS('\nOctoFit database successfully populated with test data!'))
