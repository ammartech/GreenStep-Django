from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import date, timedelta
from django.http import JsonResponse
import json

from .models import Activity, EmissionFactor, UserProfile
from .forms import ActivityForm, UserRegistrationForm

def home(request):
    """Homepage with overview stats"""
    context = {}
    if request.user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        today_emissions = profile.get_daily_emissions()
        week_emissions = profile.get_weekly_emissions()

        # Calculate goal percentage safely
        goal_percentage = 0
        if profile.daily_goal > 0:
            goal_percentage = (today_emissions / profile.daily_goal) * 100

        # Calculate over goal amount
        over_goal = max(0, today_emissions - profile.daily_goal)

        context.update({
            'today_emissions': round(today_emissions, 2),
            'week_emissions': round(week_emissions, 2),
            'daily_goal': profile.daily_goal,
            'goal_percentage': round(goal_percentage, 1),
            'over_goal': round(over_goal, 1),
        })

    return render(request, 'tracker/home.html', context)

@login_required
def dashboard(request):
    """Main dashboard with detailed analytics"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Get recent activities
    recent_activities = Activity.objects.filter(user=request.user)[:10]

    # Calculate weekly data for chart
    weekly_data = []
    for i in range(7):
        target_date = date.today() - timedelta(days=i)
        daily_total = profile.get_daily_emissions(target_date)
        weekly_data.append({
            'date': target_date.strftime('%a'),
            'emissions': round(daily_total, 2)
        })
    weekly_data.reverse()

    # Category breakdown
    categories = EmissionFactor.objects.values('category').distinct()
    category_data = []
    for cat in categories:
        category_name = cat['category']
        total = Activity.objects.filter(
            user=request.user,
            emission_factor__category=category_name,
            date__gte=date.today() - timedelta(days=30)
        ).aggregate(
            total=Sum('quantity') * Sum('emission_factor__co2_per_unit')
        )['total'] or 0

        if total > 0:
            category_data.append({
                'category': category_name.title(),
                'total': round(total, 2)
            })

    context = {
        'profile': profile,
        'recent_activities': recent_activities,
        'weekly_data': json.dumps(weekly_data),
        'category_data': json.dumps(category_data),
        'today_emissions': round(profile.get_daily_emissions(), 2),
        'week_emissions': round(profile.get_weekly_emissions(), 2),
    }

    return render(request, 'tracker/dashboard.html', context)

@login_required
def add_activity(request):
    """Add new activity"""
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user
            activity.save()
            messages.success(request, f'Activity added! CO₂ impact: {activity.co2_emissions:.2f} kg')
            return redirect('dashboard')
    else:
        form = ActivityForm()

    return render(request, 'tracker/add_activity.html', {'form': form})

@login_required
def activities_list(request):
    """List all user activities with filtering"""
    activities = Activity.objects.filter(user=request.user)

    # Filter by category if specified
    category = request.GET.get('category')
    if category:
        activities = activities.filter(emission_factor__category=category)

    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        activities = activities.filter(date__gte=date_from)
    if date_to:
        activities = activities.filter(date__lte=date_to)

    context = {
        'activities': activities,
        'categories': EmissionFactor.CATEGORY_CHOICES,
        'selected_category': category,
        'date_from': date_from,
        'date_to': date_to,
    }

    return render(request, 'tracker/activities_list.html', context)

@login_required
def delete_activity(request, activity_id):
    """Delete an activity"""
    activity = get_object_or_404(Activity, id=activity_id, user=request.user)
    if request.method == 'POST':
        activity.delete()
        messages.success(request, 'Activity deleted successfully!')
    return redirect('activities_list')

def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Welcome to GreenSteps! Start tracking your carbon footprint today.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def api_weekly_data(request):
    """API endpoint for weekly emissions data"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    weekly_data = []
    for i in range(7):
        target_date = date.today() - timedelta(days=i)
        daily_total = profile.get_daily_emissions(target_date)
        weekly_data.append({
            'date': target_date.strftime('%Y-%m-%d'),
            'day': target_date.strftime('%a'),
            'emissions': round(daily_total, 2)
        })

    return JsonResponse({'data': weekly_data[::-1]})

@login_required
def tips(request):
    """Sustainability tips based on user's highest emission categories"""
    # Find user's top emission categories from last 30 days
    thirty_days_ago = date.today() - timedelta(days=30)
    top_categories = Activity.objects.filter(
        user=request.user,
        date__gte=thirty_days_ago
    ).values('emission_factor__category').annotate(
        total=Sum('quantity')
    ).order_by('-total')[:3]

    # Define tips for each category
    tips_data = {
        'transport': [
            "Try walking or cycling for trips under 2km",
            "Use public transport instead of driving alone",
            "Consider carpooling for longer journeys",
            "Work from home when possible to reduce commuting",
        ],
        'energy': [
            "Switch to LED light bulbs",
            "Unplug electronics when not in use",
            "Set your thermostat 1-2 degrees lower in winter",
            "Use energy-efficient appliances",
        ],
        'food': [
            "Try 'Meatless Monday' or reduce meat consumption",
            "Buy local and seasonal produce",
            "Reduce food waste by meal planning",
            "Choose organic options when possible",
        ],
        'digital': [
            "Stream videos in lower quality when possible",
            "Reduce email subscriptions and delete unused accounts",
            "Use cloud storage efficiently",
            "Choose dark mode to save device energy",
        ]
    }

    personalized_tips = []
    for cat_data in top_categories:
        category = cat_data['emission_factor__category']
        if category in tips_data:
            personalized_tips.extend(tips_data[category])

    # Add general tips if no specific categories found
    if not personalized_tips:
        personalized_tips = [
            "Start tracking your daily activities to identify improvement areas",
            "Set a daily CO₂ goal and try to stay under it",
            "Make one small sustainable change each week",
            "Share your progress with friends to stay motivated",
        ]

    context = {
        'tips': personalized_tips[:8],  # Show max 8 tips
        'top_categories': [cat['emission_factor__category'].title() for cat in top_categories]
    }

    return render(request, 'tracker/tips.html', context)
