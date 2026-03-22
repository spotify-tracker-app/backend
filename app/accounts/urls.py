from django.urls import path
from .views import AuthenticationURL, SpotifyCallback, CheckAuthentication, CurrentSpotifyUser

urlpatterns = [
    path('login/', AuthenticationURL.as_view(), name='spotify-login'),
    path('callback/', SpotifyCallback.as_view(), name='spotify-callback'),
    path('is-authenticated/', CheckAuthentication.as_view(), name='spotify-is-authenticated'),
    path('me/', CurrentSpotifyUser.as_view(), name='spotify-me')
]