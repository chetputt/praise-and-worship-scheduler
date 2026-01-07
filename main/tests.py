from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Song, Schedule

# Create your tests here.

class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="testpassword")

    def test_login_success(self):
        response = self.client.post(reverse("login"), {
            "userInput": "test",
            "passInput": "testpassword"
        })
        self.assertRedirects(response, reverse("home"))

    def test_login_failure(self):
        response = self.client.post(reverse("login"), {
            "userInput": "wrong",
            "passInput": "wrongpassword"
        })
        self.assertContains(response, "Incorrect username or password")


class SongsTests(TestCase):
    def setUp(self):
        self.test_song = Song.objects.create(name="test_song", key="C", frequency=4, hymn=False)

    def test_add_song(self):
        response = self.client.post(reverse("songs"), {
            "name": "newSong",
            "keys_dropdown": "A",
            "freq_input": 2,
            "hymn_checkbox": "on",
            "addSongBtn": "Add"
        }, follow=True)

        song = Song.objects.get(name="newSong")
        self.assertEqual(song.name, "newSong")
        self.assertEqual(song.key, "A")
        self.assertEqual(song.frequency, 2)
        self.assertTrue(song.hymn)
        self.assertContains(response, "Successfully added song")

    def test_edit_key(self):
        response = self.client.post(reverse("songs"), {
            "edit_song_dropdown": "test_song",
            "keys_dropdown": "B",
            "editSongBtn":"Key"
        }, follow=True)
        song = Song.objects.first()
        self.assertEqual(song.key, "B")
        self.assertContains(response, "Successfully edited key")

    def test_edit_key_fail(self):
        response = self.client.post(reverse("songs"), {
            "edit_song_dropdown": "notAsong",
            "keys_dropdown": "B",
            "editSongBtn":"Key"
        }, follow=True)
        self.assertContains(response, "Cannot edit the key of an invalid song")

    def test_edit_frequency(self):
        response = self.client.post(reverse("songs"), {
            "freq_dropdown": "test_song",
            "edit_freq_input": 5,
            "freqBtn": "Freq"
        }, follow=True)
        song = Song.objects.first()
        self.assertEqual(song.frequency, 5)
        self.assertContains(response, "Successfully edited frequency")
    
    def test_edit_frequency_fail(self):
        response = self.client.post(reverse("songs"), {
            "freq_dropdown": "notAsong",
            "edit_freq_input": 5,
            "freqBtn": "Freq"
        }, follow=True)
        self.assertContains(response, "Cannot edit the frequency of an invalid song")

    def test_delete_song(self):
        response = self.client.post(reverse("songs"), {
            "delete_song_dropdown": "test_song",
            "deleteSongBtn": "Delete"
        }, follow=True)
        self.assertFalse(Song.objects.filter(name="test_song").exists())
        self.assertContains(response, "Successfully deleted song")
    
    def test_delete_song_fail(self):
        response = self.client.post(reverse("songs"), {
            "delete_song_dropdown": "notAsong",
            "deleteSongBtn": "Delete"
        }, follow=True)
        self.assertContains(response, "Failed to delete song")

    def test_song_dupe(self):
        response = self.client.post(reverse("songs"), {
            "name": "test_song",
            "keys_dropdown": "A",
            "freq_input": 2,
            "hymn_checkbox": "on",
            "addSongBtn": "Add"
        }, follow=True)
        self.assertTrue(Song.objects.filter(name="test_song").count() == 1)
        self.assertContains(response, "There is already a song with this name or name input is empty")

    def test_no_name(self):
        response = self.client.post(reverse("songs"), {
            "name": "      ",
            "keys_dropdown": "A",
            "freq_input": 2,
            "hymn_checkbox": "on",
            "addSongBtn": "Add"
        }, follow=True)
        self.assertTrue(Song.objects.filter(name="test_song").count() == 1)
        self.assertContains(response, "There is already a song with this name or name input is empty")


class EditTests(TestCase):

    # the Django default date format is "Y-m-d"
    def setUp(self):
        self.song1 = Song.objects.create(name="song1", key="A", frequency=2, hymn=True)
        self.song2 = Song.objects.create(name="song2", key="D", frequency=4, hymn=False)
        self.song3 = Song.objects.create(name="song3", key="F", frequency=1, hymn=True)
        self.test_schedule = Schedule.objects.create(date="2025-06-18")
        
        self.test_schedule.songs.add(self.song1)
        self.test_schedule.songs.add(self.song2)
        self.test_schedule.songs.add(self.song3)

    def test_add_schedule(self):
        response = self.client.post(reverse("edit"), {
            "date": "2024-12-12",
            "first_song_dropdown": "song1",
            "second_song_dropdown": "song2",
            "third_song_dropdown": "song3",
            "addScheduleBtn": "Add"
        }, follow=True)
        self.assertTrue(Schedule.objects.filter(date="2024-12-12").exists())
        schedule = Schedule.objects.get(date="2024-12-12")
        self.assertEqual(schedule.songs.count(), 3)
        self.assertContains(response, "Successfully added schedule")
        
    def test_delete_schedule(self):

        # the dropdown date format is m-d-Y but the Schedule model date format is Y-m-d
        response = self.client.post(reverse("edit"), {
            "schedule_dropdown": "06-18-2025",
            "deleteScheduleBtn": "Delete"
        }, follow=True)
        self.assertFalse(Schedule.objects.filter(date="2025-06-18").exists())
        self.assertContains(response, "Successfully deleted schedule")

    # test for scheduled and last_scheduled variables of the song model
    def test_delete_schedule_song_dates(self):
        Song.objects.filter(name="song1").update(last_scheduled="2025-01-01")

        response = self.client.post(reverse("edit"), {
            "schedule_dropdown": "06-18-2025",
            "deleteScheduleBtn": "Delete"
        }, follow=True)

        # last_scheduled became scheduled now
        self.assertTrue(str(Song.objects.get(name="song1").scheduled) == "2025-01-01")

    def test_empty_schedule(self):
        response = self.client.post(reverse("edit"), {
            "date": "2024-12-12",
            "first_song_dropdown": "song1",
            "second_song_dropdown": "song2",
            "third_song_dropdown": "",
            "addScheduleBtn": "Add"
        }, follow=True)
        self.assertFalse(Schedule.objects.filter(date="2024-12-12").exists())
        self.assertContains(response, "Failed to add schedule: invalid song(s)")

    def test_schedule_dupe(self):
        response = self.client.post(reverse("edit"), {
            "date": "2025-06-18",
            "first_song_dropdown": "song1",
            "second_song_dropdown": "song2",
            "third_song_dropdown": "song3",
            "addScheduleBtn": "Add"
        }, follow=True)
        self.assertTrue(Schedule.objects.filter(date="2025-06-18").count() == 1)
        self.assertContains(response, "Failed to add schedule: duplicate songs or schedule date already exists") 

class ScheduleTests(TestCase):
    
    # the Django default date format is "Y-m-d"
    def test_songs_list(self):
        self.song1 = Song.objects.create(name="song1", key="A", frequency=2, hymn=True)
        self.song2 = Song.objects.create(name="song2", key="D", frequency=4, hymn=False)
        self.song3 = Song.objects.create(name="song3", key="F", frequency=1, hymn=True)
        self.test_schedule = Schedule.objects.create(date="2025-06-18")

        self.test_schedule.songs.add(self.song1)
        self.test_schedule.songs.add(self.song2)
        self.test_schedule.songs.add(self.song3)

        response = self.client.get(reverse("schedule"))
        self.assertContains(response, '<li><a class="dropdown-item" href="#">song1</a></li>', html=True)
        self.assertContains(response, '<li><a class="dropdown-item" href="#">song2</a></li>', html=True)
        self.assertContains(response, '<li><a class="dropdown-item" href="#">song3</a></li>', html=True)