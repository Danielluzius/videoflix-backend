from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_ratelimit.decorators import ratelimit
from user_app.api.serializers import (
    RegisterSerializer, LoginSerializer,
    PasswordResetSerializer, PasswordConfirmSerializer,
)
from user_app import services
from user_app.tasks import task_send_activation_email, task_send_password_reset_email


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class RegisterView(APIView):
    """Register a new user account and send a confirmation email."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Create an inactive user and dispatch the activation email task."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = services.create_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )
        task_send_activation_email.delay(user)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        return Response(
            {'user': {'id': user.pk, 'email': user.email}, 'token': f"{uid}/{token}"},
            status=status.HTTP_201_CREATED,
        )


class ActivateView(APIView):
    """Activate a user account via the uid/token link sent by email."""

    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        """Validate the token and mark the account as active."""
        user = services.activate_user(uidb64, token)
        if not user:
            return Response({'detail': 'Activation failed.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Account successfully activated.'})


@method_decorator(ratelimit(key='ip', rate='10/m', method='POST', block=True), name='post')
class LoginView(APIView):
    """Authenticate a user and set JWT tokens as HTTP-only cookies."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validate credentials and return access_token + refresh_token cookies."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )
        if not user:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        response = Response({'detail': 'Login successful', 'user': {'id': user.pk, 'username': user.email}})
        response.set_cookie('access_token', str(refresh.access_token), httponly=True, samesite='Lax')
        response.set_cookie('refresh_token', str(refresh), httponly=True, samesite='Lax')
        return response


class LogoutView(APIView):
    """Blacklist the refresh token and clear JWT cookies."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Blacklist the refresh_token cookie and delete both auth cookies."""
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'Refresh token missing.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            pass
        response = Response({'detail': 'Logout successful! All tokens will be deleted. Refresh token is now invalid.'})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class TokenRefreshView(APIView):
    """Issue a new access token using the refresh_token cookie."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Read the refresh_token cookie and set a new access_token cookie."""
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'detail': 'Refresh token missing.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            refresh = RefreshToken(refresh_token)
            new_access = str(refresh.access_token)
        except TokenError:
            return Response({'detail': 'Invalid refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)
        response = Response({'detail': 'Token refreshed', 'access': new_access})
        response.set_cookie('access_token', new_access, httponly=True, samesite='Lax')
        return response


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class PasswordResetView(APIView):
    """Send a password reset email to the given address."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Dispatch the reset email task. Always returns 200 to avoid email enumeration."""
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = services.get_user_for_password_reset(serializer.validated_data['email'])
        if user:
            task_send_password_reset_email.delay(user)
        return Response({'detail': 'An email has been sent to reset your password.'})


class PasswordConfirmView(APIView):
    """Set a new password using the uid/token from the reset email."""

    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """Validate the reset token and update the user's password."""
        serializer = PasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = services.set_new_password(uidb64, token, serializer.validated_data['new_password'])
        if not user:
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Your Password has been successfully reset.'})
