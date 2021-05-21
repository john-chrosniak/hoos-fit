from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.urls import reverse
from django.views import generic
import datetime
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from .forms import CreateNewExercise, CreateNewWorkout
from .models import Exercise, Workout, Award, Profile
import random


motivations=[
'"Create a Positive Environment"',
 '"The Best Way To Get Started Is To Quit Talking And Begin Doing"',
 '"Don’t Let Yesterday Take Up Too Much Of Today"',
'"We May Encounter Many Defeats But We Must Not Be Defeated"',
'"We Generate Fears While We Sit. We Overcome Them By Action"',
'"Whether You Think You Can Or Think You Can’t, You’re Right"',
'"Do What You Can With All You Have, Wherever You Are"',
'"No pain, no gain. Shut up and train"',
'"Your body can stand almost anything. It’s your mind that you have to convince"',
'"Train insane or remain the same"',
'"Push yourself because no one else is going to do it for you"',
'"Suck it up. And one day you won’t have to suck it in."',
'"Success starts with self-discipline"',
'"Good things come to those who sweat"',
'"A one hour workout is 4 percent of your day. No excuses."',
'"The body achieves what the mind believes"',
'"What seems impossible today will one day become your warm-up"',
'"Hustle for that muscle"',
'"The hardest lift of all is lifting your butt off the couch."',
'"When you feel like quitting think about why you started"',
]


# Create your views here.
# @login_required
def home(request):
    if request.user.username != "":
        return HttpResponseRedirect(
                    reverse(profile,
                    args=[request.user.username]))
    else:
        return render(request, 'hoosfit/index.html')


def profile(request, user_id):
    if request.user.profile.previous_workout < (datetime.date.today() - datetime.timedelta(days=1)):
        request.user.profile.streak_number = 0
        request.user.profile.save()
    context={}
    context['quote']=random.choice(motivations)
    weekExercises = Exercise.objects.filter(user__exact = request.user, date__lte=datetime.datetime.today(), date__gte=datetime.datetime.today()-datetime.timedelta(days=7))
    context['weekExercises']=weekExercises
    return render(request, 'hoosfit/profile.html', context)

class ExerciseCreate(generic.ListView):
    model = Exercise
    template_name = 'hoosfit/exercise.html'

class WorkoutCreate(generic.ListView):
    model = Workout
    template_name = 'hoosfit/workout.html'
    context_object_name = 'exercise_list'

    def get_queryset(self):
        return Exercise.objects.filter(user__exact = self.request.user, date=datetime.date(2000,1,1))

class ExerciseView(generic.ListView):
    template_name = 'hoosfit/view_exercise.html'
    context_object_name = 'exercise_list'

    def get_queryset(self):
        return Exercise.objects.filter(user__exact = self.request.user, date=datetime.date(2000,1,1))


class WorkoutListView(generic.ListView):
    template_name = 'hoosfit/view_workouts.html'
    context_object_name = 'workout_list'

    def get_queryset(self):
        return Workout.objects.filter(user__exact = self.request.user)


class WorkoutView(generic.DetailView):
    model = Workout
    template_name = 'hoosfit/workout_form.html'
    context_object_name = 'workout'

    
class WorkoutSummary(generic.ListView):
    template_name = 'hoosfit/workout_summary.html'
    context_object_name = 'workout'

    def get_queryset(self):
        return Exercise.objects.filter(user__exact = self.request.user, date=datetime.date.today())


class AwardView(generic.ListView):
    model = Award
    template_name = 'hoosfit/view_awards.html'
    context_object_name = 'awards'

    def get_queryset(self):
        return Award.objects.filter(user__exact = self.request.user)


class LeaderboardView(generic.ListView):
    template_name = 'hoosfit/leaderboard.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        return Profile.objects.order_by('-points')


def create_exercise(request, user_id):
    context = {}
    if request.method == "POST":
        form = CreateNewExercise(request.POST)
        if form.is_valid():
            ex = Exercise.objects.filter(user__exact = request.user, exercise_name__iexact = request.POST['exercise_name'])
            if ex.count() == 0:
                exercise = form.save(commit=False)
                exercise.user = request.user
                exercise.save()
        else:
            pass
    return HttpResponseRedirect(reverse('exerciseview', kwargs={'user_id' : user_id}))


def create_workout(request, user_id):
    if request.method == "POST":
        form = CreateNewWorkout(request.POST)
        if form.is_valid() and request.POST.get('exercises', False):
            workout = form.save(commit=False)
            workout.user = request.user
            workout.save()
            for id_ in request.POST.getlist('exercises'):
                exercise = Exercise.objects.get(user=request.user, id=id_, date=datetime.date(2000,1,1))
                workout.exercises.add(exercise)
        else:
            pass
    return HttpResponseRedirect(reverse('workoutstart', kwargs={'user_id' : user_id, 'pk' : workout.id}))


def log_workout(request, user_id, pk):
    for data in request.POST:
        try:  # saves exercise and streak data
            name = data
            reps = request.POST[data]
            profile = Profile.objects.get(user=request.user)
            profile.points += int(reps)
            if profile.previous_workout < datetime.date.today():
                profile.streak_number += 1
            profile.previous_workout = datetime.date.today()
            profile.save()
            exercise = Exercise()
            exercise.exercise_name = name
            exercise.reps = reps
            exercise.user = request.user
            exercise.date = datetime.date.today()
            exercise.save()
        except: # error occurs due to weird packet information (REST thing)
            continue  # don't care scenario
        try: # award already exists
            award = Award.objects.get(user=request.user, exercise_name=data)
            if award.best_reps < int(request.POST[data]):
                award.best_reps = request.POST[data]
                award.save()
        except Award.DoesNotExist:
            award = Award()
            award.user = request.user
            award.award_name = "Personal Best: "+ data
            award.exercise_name = data
            award.best_reps = request.POST[data]
            award.save()
    return HttpResponseRedirect(reverse('workoutsummary', kwargs={'user_id' : user_id, 'pk' : pk}))