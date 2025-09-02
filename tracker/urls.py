from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_activity, name='add_activity'),
    path('activities/', views.activities_list, name='activities_list'),
    path('activities/delete/<int:activity_id>/', views.delete_activity, name='delete_activity'),
    path('tips/', views.tips, name='tips'),
    path('register/', views.register, name='register'),
    path('api/weekly-data/', views.api_weekly_data, name='api_weekly_data'),
]
