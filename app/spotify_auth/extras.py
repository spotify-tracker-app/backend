from .models import Token
from django.utils import timezone
from datetime import timedelta
from requests import post
from .credentials import CLIENT_ID, CLIENT_SECRET


BASE_URL = "https://api.spotify.com/v1/me/"


def check_tokens(app_token):
    tokens = Token.objects.filter(user=app_token)
    
    if not tokens:
        return None
    
    
    if tokens[0].expires_in <= timezone.now():
        refresh_token_func(app_token)
        return Token.objects.filter(user=app_token)[0]
    
    return tokens[0]
        
    
def create_or_update_tokens(app_token, access_token, refresh_token, expires_in, token_type):
    token_obj = check_tokens(app_token)
    expires_in = timezone.now() + timedelta(seconds=expires_in)

    if token_obj:
        token_obj.access_token = access_token
        if refresh_token:
            token_obj.refresh_token = refresh_token
        token_obj.expires_in = expires_in
        token_obj.token_type = token_type
        token_obj.save(update_fields=['access_token', 'refresh_token', 'expires_in', 'token_type'])
    else:
        Token.objects.create(
            user=app_token, 
            access_token=access_token, 
            refresh_token=refresh_token, 
            expires_in=expires_in, 
            token_type=token_type
        )
       
        
def is_spotify_authenticated(app_token):
    token_obj = check_tokens(app_token)
    
    if token_obj:
        if token_obj.expires_in <= timezone.now():
            refresh_token_func(app_token)
        return True
    return False


def refresh_token_func(app_token):
    token_obj = check_tokens(app_token)
    if not token_obj or not token_obj.refresh_token:
        return
    
    response = post("https://accounts.spotify.com/api/token", data={
        "grant_type": "refresh_token",
        "refresh_token": token_obj.refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }).json()
    
    access_token = response.get("access_token")
    expires_in = response.get("expires_in")
    token_type = response.get("token_type")
    
    new_refresh_token = response.get("refresh_token", token_obj.refresh_token)
    
    create_or_update_tokens(
        app_token=app_token, 
        access_token=access_token, 
        refresh_token=new_refresh_token, 
        expires_in=expires_in, 
        token_type=token_type
    )
    
def get_app_token(request):
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Token '):
        return auth_header.split(' ')[1]
    return None