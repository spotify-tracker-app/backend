from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .extras import check_tokens

class SpotifyAppAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        app_token = auth_header.split(' ')[1]
        token_obj = check_tokens(app_token)
        if not token_obj:
            raise AuthenticationFailed('Invalid or expired token')
        
        return (app_token, token_obj)