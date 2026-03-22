from rest_framework import response
from rest_framework.views import APIView
from rest_framework import status
from requests import get
from django.shortcuts import render
from spotify_auth.extras import check_tokens, get_app_token

# Create your views here.
def fetch_from_spotify(request, endpoint):
    app_token = get_app_token(request)
    if not app_token:
        return None, response.Response({"Error": "Authentication token not provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    token_obj = check_tokens(app_token)
    if not token_obj:
        return None, response.Response({"Error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token_obj.access_token}"
    }
    
    spotify_response = get(f"https://api.spotify.com/v1/{endpoint}", headers=headers)
    
    if spotify_response.status_code == 200:
        return spotify_response.json(), None
    
    return None, response.Response({"Error": f"Failed to fetch data from Spotify for endpoint: {endpoint}"}, status=status.HTTP_400_BAD_REQUEST)

class LastPlayed(APIView):
    def get(self, request, format=None):
        data, error_response = fetch_from_spotify(request, "me/player/recently-played?limit=10")
        if error_response:
            return error_response
        return response.Response(data, status=status.HTTP_200_OK)
    
class PlayedStats(APIView):
    def get(self, request, format=None):
        time_range = request.GET.get('time_range', 'short_term') 
        if time_range not in ['short_term', 'medium_term', 'long_term']:
            return response.Response({"Error": "Invalid time range. Use 'short_term', 'medium_term', or 'long_term'."}, status=status.HTTP_400_BAD_REQUEST)
        
        tracks_data, tracks_error = fetch_from_spotify(request, f"me/top/tracks?time_range={time_range}&limit=10")
        if tracks_error:
            return tracks_error
        
        artists_data, artists_error = fetch_from_spotify(request, f"me/top/artists?time_range={time_range}&limit=10")
        if artists_error:
            return artists_error
    
        return response.Response({
            "time_range": time_range,
            "top_tracks": tracks_data.get("items", []),
            "top_artists": artists_data.get("items", [])
        }, status=status.HTTP_200_OK)
        
class AccountInfo(APIView):
    def get(self, request, format=None):
        data, error_response = fetch_from_spotify(request, "me")
        if error_response:
            return error_response
        return response.Response(data, status=status.HTTP_200_OK)
    
    
        
        