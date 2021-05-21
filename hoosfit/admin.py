from django.contrib import admin

# Register your models here.
from .models import Exercise, Workout, Award, Profile

admin.site.register(Exercise)
admin.site.register(Workout)
admin.site.register(Award)
admin.site.register(Profile)