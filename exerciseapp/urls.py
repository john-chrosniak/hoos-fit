"""exerciseapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from hoosfit.views import home, profile, create_exercise, create_workout, ExerciseCreate, ExerciseView, WorkoutCreate, AwardView, WorkoutView, log_workout, WorkoutSummary, WorkoutListView, LeaderboardView

app_name = 'exerciseapp'
urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('profiles/home/', home),
    path('profiles/<str:user_id>/', profile, name='homepage'),
    path('profiles/<str:user_id>/exercise/', ExerciseCreate.as_view(), name='exercisecreate'),
    path('profiles/<str:user_id>/exercise/submit/', create_exercise, name='exercisesubmit'),
    path('profiles/<str:user_id>/exercise/view/', ExerciseView.as_view(), name='exerciseview'),
    path('profiles/<str:user_id>/workout/', WorkoutCreate.as_view(), name='workoutcreate'),
    path('profiles/<str:user_id>/workout/view/', WorkoutListView.as_view(), name='workoutview'),
    path('profiles/<str:user_id>/workout/submit/', create_workout, name='workoutsubmit'),
    path('profiles/<str:user_id>/workout/<int:pk>/', WorkoutView.as_view(), name='workoutstart'),
    path('profiles/<str:user_id>/workout/<int:pk>/submit/', log_workout, name='workoutend'),
    path('profiles/<str:user_id>/workout/<int:pk>/summary/', WorkoutSummary.as_view(), name='workoutsummary'),
    path('profiles/<str:user_id>/awards/', AwardView.as_view(), name='awardview'),
    path('leaderboard', LeaderboardView.as_view(), name='leaderboard')
]
