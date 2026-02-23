from django.shortcuts import render
from app.accounts.extras import create_or_update_tokens, is_spotify_authenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import response
from requests import Request, posixpath
from django.http import HttpResponseRedirect
from .credentials import CLIENT_ID, CLINET_SECRET, CLIENT_URI

class AuthenticationURL(APIView):
    def get(self, request, format=None):
        scopes = "user-read_currently_playing user-read-playback-state user-modify-playback-state user-library-read user-follow-read playlist-read-private playlist-read-collaborative"
        url = Request("GET", "https://accounts.spotify.com/authorize", params={
            "scope": scopes,
            "response_type": "code",
            "redirect_uri": CLIENT_URI,
            "client_id": CLIENT_ID
        }).prepare().url
        return HttpResponseRedirect(url)

def spotify_redirect(request, format=None):
    code = request.GET.get("code")
    error = request.GET.get("error")
    if error:
        return response.Response({"Error": "Authorization failed"}, status=status.HTTP_400_BAD_REQUEST)

    response = post('https://accounts.spotify.com/api/token', data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": CLIENT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLINET_SECRET
    }).json()
    
    access_token = response.get("access_token")
    refresh_token = response.get("refresh_token")
    expires_in = response.get("expires_in")
    token_type = response.get("token_type")
    
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
    
    redirect_url = ""
    return HttpResponseRedirect(redirect_url)

class CheckAuthentication(APIView):
    def get(self, request, format=None):
        key = self.request.session.session_key
        if not self.request.session.exists(key):
            self.request.session.create()
            key = self.request.session.session_key
        
        auth_status = is_spotify_authenticated(key)
        
        if auth_status:
            redirect_url = ""
            return HttpResponseRedirect(redirect_url)
        else:
            redirect_url = ""
            return HttpResponseRedirect(redirect_url)