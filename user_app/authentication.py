from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class CookieJWTAuthentication(JWTAuthentication):
    """Custom JWT authentication that reads the access token from an HTTP-only cookie."""

    def authenticate(self, request):
        """Extract and validate the access token from the 'access_token' cookie.

        Returns None if the cookie is absent, so other authenticators can take over.
        """
        access_token = request.COOKIES.get('access_token')
        if access_token is None:
            return None
        try:
            validated_token = self.get_validated_token(access_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, TokenError):
            return None
