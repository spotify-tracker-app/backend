from django.shortcuts import render
from .extras import create_or_update_tokens, is_spotify_authenticated, check_tokens
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import response
from requests import Request, post, get
from django.http import HttpResponseRedirect
from .credentials import CLIENT_ID, CLIENT_SECRET, CLIENT_URI

class AuthenticationURL(APIView):
    def get(self, request, format=None):
        scopes = "user-read-currently-playing user-read-playback-state"
        url = Request("GET", "https://accounts.spotify.com/authorize", params={
            "scope": scopes,
            "response_type": "code",
            "redirect_uri": CLIENT_URI,
            "client_id": CLIENT_ID
        }).prepare().url
        return response.Response({"url": url}, status=status.HTTP_200_OK)

def spotify_redirect(request, format=None):
    code = request.GET.get("code")
    error = request.GET.get("error")
    if error:
        return response.Response({"Error": "Authorization failed"}, status=status.HTTP_400_BAD_REQUEST)

    api_response = post('https://accounts.spotify.com/api/token', data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": CLIENT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }).json()
    
    access_token = api_response.get("access_token")
    refresh_token = api_response.get("refresh_token")
    expires_in = api_response.get("expires_in")
    token_type = api_response.get("token_type")
    
    authKey = request.session.session_key
    if not request.session.exists(authKey):
        request.session.create()
        authKey = request.session.session_key
        
    create_or_update_tokens(
        session_id=authKey, 
        access_token=access_token, 
        refresh_token=refresh_token, 
        expires_in=expires_in, 
        token_type=token_type
    )
    
    redirect_url = "http://127.0.0.1:8000/auth/me/"
    return HttpResponseRedirect(redirect_url)

class CheckAuthentication(APIView):
    def get(self, request, format=None):
        key = self.request.session.session_key
        if not self.request.session.exists(key):
            self.request.session.create()
            key = self.request.session.session_key
        
        auth_status = is_spotify_authenticated(key)
        
        return response.Response({'status': auth_status}, status=status.HTTP_200_OK)
    
class CurrentSpotifyUser(APIView):
    def get(self, request, format=None):
        if not request.session.exists(request.session.session_key):
            request.session.create()
        session_id = request.session.session_key
        token_obj = check_tokens(session_id)
        if not token_obj:
            return response.Response({"Error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token_obj.access_token}"
        }
        
        spotify_response = get("https://api.spotify.com/v1/me", headers=headers)
        
        if spotify_response.status_code != 200:
            return response.Response({"Error": "Failed to fetch user data"}, status=spotify_response.status_code)
        
        return response.Response(spotify_response.json(), status=status.HTTP_200_OK)