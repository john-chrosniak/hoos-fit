from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Exercise, Award, Workout
import datetime


class ExerciseTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='password')
        self.user2 = User.objects.create_user(username='testuser2', password='password')
        self.user3 = User.objects.create_user(username='testuser3', password='password')
        self.user4 = User.objects.create_user(username='testuser4', password='password')

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.user3.delete()
        self.user4.delete()
    
    def test_no_exercises(self):
        """
        Tests if an error message is shown when a user has no exercises
        """
        client = Client()
        client.login(username='testuser1', password='password')
        response = client.get(reverse('exerciseview', kwargs={'user_id' : self.user1.username}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No exercises created yet :(")
        self.assertQuerysetEqual(response.context['exercise_list'], [])

    def test_exercise_save(self):
        """
        Tests if exercises are saved correctly
        """
        client = Client()
        client.login(username='testuser2', password='password')
        response = client.post('/profiles/{0}/exercise/submit/'.format(self.user2.username), {'user': [self.user2], 'exercise_name': ['Push Up']}, follow=True)
        qs = Exercise.objects.filter(user__exact = self.user2, date=datetime.date(2000,1,1))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(qs.count(), 1)

    def test_exercise_view(self):
        """
        Tests if exercises are correctly displayed in exercise view
        """
        client = Client()
        client.login(username='testuser3', password='password')
        exercise1 = Exercise.objects.create(exercise_name='Push Up', user=self.user3)
        exercise2 = Exercise.objects.create(exercise_name='Squat', user=self.user3)
        response = client.get(reverse('exerciseview', kwargs={'user_id' : self.user3.username}))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['exercise_list'], [repr(exercise1), repr(exercise2)], ordered=False)

    def test_duplicate_exercises(self):
        """
        Tests that no duplicate exercises are saved
        """
        client = Client()
        client.login(username='testuser4', password='password')
        response1 = client.post('/profiles/{0}/exercise/submit/'.format(self.user4.username), {'user': [self.user4], 'exercise_name': ['Push Up']}, follow=True)
        response2 = client.post('/profiles/{0}/exercise/submit/'.format(self.user4.username), {'user': [self.user4], 'exercise_name': ['Squat']}, follow=True)
        response3 = client.post('/profiles/{0}/exercise/submit/'.format(self.user4.username), {'user': [self.user4], 'exercise_name': ['Push Up']}, follow=True)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 200)
        get_response = client.get(reverse('exerciseview', kwargs={'user_id' : self.user4.username}))
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.context['exercise_list'].count(), 2)
    

class WorkoutTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='password')
        self.user2 = User.objects.create_user(username='testuser2', password='password')
        self.user3 = User.objects.create_user(username='testuser3', password='password')
        self.user4 = User.objects.create_user(username='testuser4', password='password')

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.user3.delete()
        self.user4.delete()

    def test_workout_save(self):
        """
        Tests if workouts are saved correctly
        """
        client = Client()
        client.login(username='testuser1', password='password')
        exercise1 = Exercise.objects.create(exercise_name='Push Up', user=self.user1)
        exercise2 = Exercise.objects.create(exercise_name='Squat', user=self.user1)
        response = client.post('/profiles/{0}/workout/submit/'.format(self.user1.username), {'workout_name': ['Test Workout'], 'exercises': [exercise1.id, exercise2.id]}, follow=True)
        workout = Workout.objects.get(user__exact = self.user1, date=datetime.date.today(), workout_name='Test Workout')
        exercise_qs = Exercise.objects.filter(user__exact = self.user1, date=datetime.date.today())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(workout.workout_name, "Test Workout")
        self.assertQuerysetEqual(workout.exercises.all(), [repr(exercise1), repr(exercise2)], ordered=False)

    def test_logging_workout(self):
        """
        Tests if exercises with reps were saved after logging workout
        """
        client = Client()
        client.login(username='testuser2', password='password')
        exercise1 = Exercise.objects.create(exercise_name='Push Up', user=self.user2)
        exercise2 = Exercise.objects.create(exercise_name='Squat', user=self.user2)
        response1 = client.post('/profiles/{0}/workout/submit/'.format(self.user2.username), {'workout_name': ['Test Workout'], 'exercises': [exercise1.id, exercise2.id]}, follow=True)
        workout = Workout.objects.get(user__exact = self.user2, date=datetime.date.today(), workout_name='Test Workout')
        response2 = client.post('/profiles/{0}/workout/{1}/submit/'.format(self.user2.username, workout.id), {'Push Up': 10, 'Squat': 10}, follow=True)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        exercise_qs = Exercise.objects.filter(user__exact=self.user2, date=datetime.date.today())
        self.assertQuerysetEqual(exercise_qs, [repr(exercise1), repr(exercise2)], ordered=False)
        pushup = Exercise.objects.get(user__exact=self.user2, date=datetime.date.today(), exercise_name='Push Up')
        squat = Exercise.objects.get(user__exact=self.user2, date=datetime.date.today(), exercise_name='Squat')
        self.assertEqual(pushup.reps, 10)
        self.assertEqual(squat.reps, 10)

    def test_workout_view(self):
        """
        Tests if workouts are correctly displayed in exercise view
        """
        client = Client()
        client.login(username='testuser3', password='password')
        exercise1 = Exercise.objects.create(exercise_name='Push Up', user=self.user3)
        workout1 = Workout.objects.create(user = self.user3, date=datetime.date.today(), workout_name='Test Workout 1')
        workout1.exercises.add(exercise1)
        exercise2 = Exercise.objects.create(exercise_name='Squat', user=self.user2)
        workout2 = Workout.objects.create(user = self.user3, date=datetime.date.today(), workout_name='Test Workout 2')
        workout2.exercises.add(exercise1)
        workout2.exercises.add(exercise2)
        response = client.get(reverse('workoutview', kwargs={'user_id' : self.user3.username}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['workout_list'].count(), 2)
        self.assertQuerysetEqual(response.context['workout_list'], [repr(workout1), repr(workout2)], ordered=False)
        testworkout1 = Workout.objects.get(user__exact = self.user3, date=datetime.date.today(), workout_name='Test Workout 1')
        testworkout2 = Workout.objects.get(user__exact = self.user3, date=datetime.date.today(), workout_name='Test Workout 2')
        self.assertQuerysetEqual(testworkout1.exercises.all(), [repr(exercise1)], ordered=False)
        self.assertQuerysetEqual(testworkout2.exercises.all(), [repr(exercise1), repr(exercise2)], ordered=False)

    def test_no_workouts(self):
        """
        Tests if an error message is shown when a user has no workouts
        """
        client = Client()
        client.login(username='testuser4', password='password')
        response = client.get(reverse('workoutview', kwargs={'user_id' : self.user4.username}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No workouts created yet :(")
        self.assertQuerysetEqual(response.context['workout_list'], [])


class AwardTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='password')
        self.user2 = User.objects.create_user(username='testuser2', password='password')
        self.user3 = User.objects.create_user(username='testuser3', password='password')

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.user3.delete()

    def test_award_save(self):
        """
        Tests if awards are saved correctly
        """
        client = Client()
        client.login(username='testuser1', password='password')
        exercise1 = Exercise.objects.create(exercise_name='Push Up', user=self.user1)
        exercise2 = Exercise.objects.create(exercise_name='Squat', user=self.user1)
        workout1 = Workout.objects.create(user = self.user1, date=datetime.date.today(), workout_name='Test Workout 1')
        workout1.exercises.add(exercise1)
        workout2 = Workout.objects.create(user = self.user1, date=datetime.date.today(), workout_name='Test Workout 2')
        workout2.exercises.add(exercise1)
        workout2.exercises.add(exercise2)
        response1 = client.post('/profiles/{0}/workout/{1}/submit/'.format(self.user1.username, workout1.id), {'Push Up': 10}, follow=True)
        self.assertEqual(response1.status_code, 200)
        award = Award.objects.get(user=self.user1, award_name="Personal Best: Push Up")
        self.assertEqual(award.best_reps, 10)
        self.assertEqual(award.date, datetime.date.today())
        response2 = client.post('/profiles/{0}/workout/{1}/submit/'.format(self.user1.username, workout2.id), {'Push Up': 5, 'Squat': 10}, follow=True)
        self.assertEqual(response2.status_code, 200)
        pushup_award = Award.objects.get(user=self.user1, award_name="Personal Best: Push Up")
        squat_award =  Award.objects.get(user=self.user1, award_name="Personal Best: Squat")
        self.assertEqual(pushup_award.best_reps, 10)
        self.assertEqual(pushup_award.date, datetime.date.today())
        self.assertEqual(squat_award.best_reps, 10)
        self.assertEqual(squat_award.date, datetime.date.today())
        

    def test_award_view(self):
        """
        Tests if awards are correctly displayed in exercise view
        """
        client = Client()
        client.login(username='testuser2', password='password')
        exercise1 = Exercise.objects.create(exercise_name='Push Up', user=self.user2)
        exercise2 = Exercise.objects.create(exercise_name='Squat', user=self.user2)
        workout1 = Workout.objects.create(user = self.user2, date=datetime.date.today(), workout_name='Test Workout 1')
        workout1.exercises.add(exercise1)
        workout2 = Workout.objects.create(user = self.user2, date=datetime.date.today(), workout_name='Test Workout 2')
        workout2.exercises.add(exercise1)
        workout2.exercises.add(exercise2)
        response1 = client.post('/profiles/{0}/workout/{1}/submit/'.format(self.user2.username, workout1.id), {'Push Up': 10}, follow=True)
        response2 = client.post('/profiles/{0}/workout/{1}/submit/'.format(self.user2.username, workout2.id), {'Push Up': 5, 'Squat': 10}, follow=True)
        get_response = client.get(reverse('awardview', kwargs={'user_id' : self.user2.username}))
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.context['awards'].count(), 2)

    def test_no_awards(self):
        """
        Tests if an error message is shown when a user has no awards
        """
        client = Client()
        client.login(username='testuser3', password='password')
        response = client.get(reverse('awardview', kwargs={'user_id' : self.user3.username}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No awards earned yet :(")
        self.assertQuerysetEqual(response.context['awards'], [])