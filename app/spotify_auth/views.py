from django.shortcuts import render
from .extras import create_or_update_tokens, is_spotify_authenticated, check_tokens, get_app_token
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import response
from requests import Request, post, get
from django.http import HttpResponseRedirect
from .credentials import CLIENT_ID, CLIENT_SECRET, CLIENT_URI


class AuthenticationURL(APIView):
    def get(self, request, format=None):
        scopes = "user-read-currently-playing user-read-playback-state user-read-recently-played user-top-read user-read-private user-read-email"
        
        
        url = Request("GET", "https://accounts.spotify.com/authorize", params={
            "scope": scopes,
            "response_type": "code",
            "redirect_uri": CLIENT_URI,
            "client_id": CLIENT_ID
        }).prepare().url
        return response.Response({"url": url}, status=status.HTTP_200_OK)

class SpotifyCallback(APIView):
    def post(self, request, format=None):
        code = request.data.get("code")
        app_token = get_app_token(request)
        
        if not app_token:
            return response.Response({"Error": "Authentication token not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not code:
            return response.Response({"Error": "Authorization code not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        api_response = post('https://accounts.spotify.com/api/token', data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": CLIENT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }).json()
        
        if "error" in api_response:
            return response.Response({"Error": "Failed to retrieve access token"}, status=status.HTTP_400_BAD_REQUEST)
        
        create_or_update_tokens(
            app_token=app_token, 
            access_token=api_response.get("access_token"), 
            refresh_token=api_response.get("refresh_token"), 
            expires_in=api_response.get("expires_in"), 
            token_type=api_response.get("token_type")
        )
        
        return response.Response({"Success": "Tokens stored successfully"}, status=status.HTTP_200_OK)

class CheckAuthentication(APIView):
    def get(self, request, format=None):
        app_token = get_app_token(request)
        if not app_token:
            return response.Response({"Error": "Authentication token not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        auth_status = is_spotify_authenticated(app_token)
        return response.Response({"status": auth_status}, status=status.HTTP_200_OK)
    
class CurrentSpotifyUser(APIView):
    def get(self, request, format=None):
        app_token = get_app_token(request)
        if not app_token:
            return response.Response({"Error": "Authentication token not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        token_obj = check_tokens(app_token)
        if not token_obj:
            return response.Response({"Error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token_obj.access_token}"
        }
        
        spotify_response = get("https://api.spotify.com/v1/me", headers=headers)
        
        if spotify_response.status_code != 200:
            return response.Response({"Error": "Failed to fetch user data from Spotify"}, status=status.HTTP_400_BAD_REQUEST)
        
        return response.Response(spotify_response.json(), status=status.HTTP_200_OK)
    
class LogoutSpotifyUser(APIView):
    def post(self, request, format=None):
        app_token = get_app_token(request)
        if not app_token:
            return response.Response({"Error": "Authentication token not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        tokens = Token.objects.filter(user=app_token)
        if tokens:
            tokens.delete()
            return response.Response({"Success": "User logged out successfully"}, status=status.HTTP_200_OK)
        
        return response.Response({"Error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    