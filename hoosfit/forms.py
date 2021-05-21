from django.forms import ModelForm, ModelMultipleChoiceField, CharField, CheckboxSelectMultiple
import datetime
from .models import Exercise, Workout

class CreateNewExercise(ModelForm):
    class Meta:
        model = Exercise
        exclude = ['user', 'reps', 'date']

class CreateNewWorkout(ModelForm):
    class Meta:
        model = Workout
        exclude = ['user', 'exercises']
