from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class EmissionFactor(models.Model):
    CATEGORY_CHOICES = [
        ('transport', 'Transportation'),
        ('energy', 'Energy'),
        ('food', 'Food'),
        ('digital', 'Digital'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)  # e.g., 'km', 'kWh', 'meal', 'hour'
    co2_per_unit = models.FloatField(help_text="CO2 emissions in kg per unit")
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.co2_per_unit} kg CO2/{self.unit})"

class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emission_factor = models.ForeignKey(EmissionFactor, on_delete=models.CASCADE)
    quantity = models.FloatField(help_text="Amount in the specified unit")
    date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def co2_emissions(self):
        return self.quantity * self.emission_factor.co2_per_unit

    def __str__(self):
        return f"{self.user.username} - {self.emission_factor.name} ({self.date})"

    class Meta:
        ordering = ['-date', '-created_at']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    daily_goal = models.FloatField(default=10.0, help_text="Daily CO2 goal in kg")
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_weekly_emissions(self):
        from datetime import date, timedelta
        week_ago = date.today() - timedelta(days=7)
        activities = Activity.objects.filter(
            user=self.user,
            date__gte=week_ago
        )
        return sum(activity.co2_emissions for activity in activities)

    def get_daily_emissions(self, target_date=None):
        if target_date is None:
            target_date = timezone.now().date()
        activities = Activity.objects.filter(
            user=self.user,
            date=target_date
        )
        return sum(activity.co2_emissions for activity in activities)
