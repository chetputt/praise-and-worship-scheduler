from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.db.models import F
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .forms import AddSongTextbox, NewSchedule
from .models import Song, Schedule
from datetime import datetime

# the edit page view
def edit(request):
    all_schedules = Schedule.objects.all().order_by("date")
    all_songs = Song.objects.all().order_by("name")
    new_schedule_form = NewSchedule()

    if request.method == "POST":

        if "addScheduleBtn" in request.POST:
            new_schedule_form = NewSchedule(request.POST)

            if new_schedule_form.is_valid():
                
                # an error should occur if any of the chosen songs doesn't exist (like typed in wrong)
                try:
                    schedule_date = new_schedule_form.cleaned_data["date"]

                    song1_name = request.POST.get("first_song_dropdown")
                    song2_name = request.POST.get("second_song_dropdown")
                    song3_name = request.POST.get("third_song_dropdown")
                    
                    # no duplicate songs or duplicate dates
                    if song1_name != song2_name and song2_name != song3_name and song1_name != song3_name \
                        and Schedule.objects.filter(date=schedule_date).exists() == False:
                        song1 = Song.objects.get(name=song1_name)
                        song2 = Song.objects.get(name=song2_name)
                        song3 = Song.objects.get(name=song3_name)
                        new_schedule = Schedule(date=schedule_date)
                        new_schedule.save()
                        
                        new_schedule.songs.add(song1)
                        new_schedule.songs.add(song2)
                        new_schedule.songs.add(song3)

                        Song.objects.filter(name=song1_name).update(frequency=F("frequency") + 1)
                        Song.objects.filter(name=song2_name).update(frequency=F("frequency") + 1)
                        Song.objects.filter(name=song3_name).update(frequency=F("frequency") + 1)
                        messages.success(request, "Successfully added schedule")
                    else:
                        messages.error(request, "Failed to add schedule: duplicate songs or schedule date already exists")
                
                except:
                    messages.error(request, "Failed to add schedule: invalid song(s)")
                return redirect("edit")
        
        elif "deleteScheduleBtn" in request.POST:
            schedule_date = request.POST.get("schedule_dropdown")

            # an error should occur if there is an invalid schedule chosen (like if typed wrong)
            try:

                parsed_date = datetime.strptime(schedule_date, "%m-%d-%Y").date()

                delete_schedule = Schedule.objects.get(date=parsed_date)
                
                for song in delete_schedule.songs.all():

                    if song.frequency >= 1:
                        song.frequency -= 1
                    song.save()
                
                delete_schedule.delete()
                messages.success(request, "Successfully deleted schedule")
                
            except:
                messages.error(request, "Failed to delete schedule")
            return redirect("edit")
        
    return render(request, "main/edit.html", {"schedules": all_schedules, "songs":all_songs, "new_schedule": new_schedule_form})

def home(request):
    return render(request, "main/home.html", {})


def login_view(request):
    fail = False

    if request.method == "POST":
        name = request.POST.get("userInput")
        word = request.POST.get("passInput")
        remember_me = request.POST.get("rememberCheckbox")
        
        # check to see if the user exists in the first place
        user = authenticate(username=name, password=word)

        if user is not None:
            login(request, user)

            if remember_me == "on":
                request.session.set_expiry(1209600) #1209600 means stay logged in for 2 weeks
            else:
                request.session.set_expiry(0)
            return redirect("home")
        else:
            # this makes the error message in the login page show up
            fail = True

    return render(request, "main/login.html", {"fail":fail})


def schedule(request):
    # used to compare current dates for past and upcoming schedules
    today = timezone.now().date()

    # this shows the most recent past schedules first
    past_schedules = Schedule.objects.filter(date__lt=today).order_by('-date')

    # this shows the soonest upcoming schedules first
    upcoming_schedules = Schedule.objects.filter(date__gte=today).order_by('date')
    return render(request, "main/schedule.html", {"past_schedules": past_schedules, "upcoming_schedules": upcoming_schedules})


def songs(request):
    add_song_form = AddSongTextbox()
    if request.method == "POST":

        if "addSongBtn" in request.POST:
            add_song_form = AddSongTextbox(request.POST)

            if add_song_form.is_valid():
                song_name = add_song_form.cleaned_data["name"].strip()

                # no duplicate or empty song names can exist
                if Song.objects.filter(name__iexact=song_name).exists() or song_name == "":
                    messages.error(request, "There is already a song with this name or name input is empty")
                    return redirect("songs")
                
                edit_name = request.POST.get("keys_dropdown")
                new_freq = int(request.POST.get("freq_input"))

                if request.POST.get("hymn_checkbox"):
                    hymn_status = True
                else:
                    hymn_status = False

                try:
                    new_song = Song(name=song_name, key=edit_name, frequency=new_freq, hymn=hymn_status )
                    new_song.save()
                    messages.success(request, "Successfully added song")

                except:
                    messages.error(request, "Failed to add song")
                return redirect("songs")

        elif "deleteSongBtn" in request.POST:
            delete_name = request.POST.get("delete_song_dropdown")

            # only delete songs with valid names that aren't None (can be invalid if typed wrong)
            if Song.objects.filter(name=delete_name).exists() and delete_name != "None":
                Song.objects.filter(name=delete_name).delete()
                messages.success(request, "Successfully deleted song")
            else:
                messages.error(request, "Failed to delete song")
            return redirect("songs")
        
        elif "editSongBtn" in request.POST:
            edit_name = request.POST.get("edit_song_dropdown")
            edit_key = request.POST.get("keys_dropdown")

            # only edit the key of songs with valid names (can be invalid if typed wrong)
            if Song.objects.filter(name=edit_name).exists():
                Song.objects.filter(name=edit_name).update(key=edit_key)
                messages.success(request, "Successfully edited key")
            else:
                messages.error(request, "Cannot edit the key of an invalid song")
            return redirect("songs")
        
        elif "freqBtn" in request.POST:
            freq_song = request.POST.get("freq_dropdown")
            new_freq = request.POST.get("edit_freq_input")

            # only edit the frequency of songs with valid names (can be invalid if typed wrong)
            if Song.objects.filter(name=freq_song).exists():
                Song.objects.filter(name=freq_song).update(frequency=new_freq)
                messages.success(request, "Successfully edited frequency")
            else:
                messages.error(request, "Cannot edit the frequency of an invalid song")
            return redirect("songs")
        
    all_songs = Song.objects.all().order_by("name")
    return render(request, "main/songs.html", {"add_form":add_song_form, "songs":all_songs})