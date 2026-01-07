from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("edit/", views.edit, name="edit"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("schedule/", views.schedule, name="schedule"),
    path("songs/", views.songs, name="songs"),
    path("logs/", views.logs_view, name="logs"),
    path("random-songs/", views.get_random_songs, name="random_songs"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # for the home page image