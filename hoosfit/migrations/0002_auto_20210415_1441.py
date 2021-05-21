# Generated by Django 3.1.7 on 2021-04-15 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hoosfit', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exercise',
            name='actual_reps',
        ),
        migrations.RemoveField(
            model_name='exercise',
            name='target_reps',
        ),
        migrations.AddField(
            model_name='exercise',
            name='date',
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name='exercise',
            name='reps',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='workout',
            name='date',
            field=models.DateField(auto_now=True),
        ),
    ]
