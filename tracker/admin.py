from django.contrib import admin
from .models import EmissionFactor, Activity, UserProfile

@admin.register(EmissionFactor)
class EmissionFactorAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'co2_per_unit', 'unit']
    list_filter = ['category']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'emission_factor', 'quantity', 'co2_emissions', 'date']
    list_filter = ['emission_factor__category', 'date', 'emission_factor']
    search_fields = ['user__username', 'emission_factor__name', 'notes']
    date_hierarchy = 'date'
    readonly_fields = ['co2_emissions', 'created_at']

    def co2_emissions(self, obj):
        return f"{obj.co2_emissions:.2f} kg"
    co2_emissions.short_description = 'CO₂ Emissions'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'daily_goal', 'location', 'created_at']
    search_fields = ['user__username', 'user__email', 'location']
    readonly_fields = ['created_at']
