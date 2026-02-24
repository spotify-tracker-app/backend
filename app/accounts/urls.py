from django.urls import path
from .views import AuthenticationURL, CurrentSpotifyUser, spotify_redirect, CheckAuthentication

urlpatterns = [
    path('login/', AuthenticationURL.as_view(), name='spotify-login'),
    path('callback/', spotify_redirect, name='spotify-callback'),
    path('is-authenticated/', CheckAuthentication.as_view(), name='spotify-is-authenticated'),
    path('me/', CurrentSpotifyUser.as_view(), name='spotify-me')
]