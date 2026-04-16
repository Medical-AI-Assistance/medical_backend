from rest_framework import status, generics
from core import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.utils import timezone
from users_auth.serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer, 
    ChangePasswordSerializer
)
from core.authentication import CookieJWTAuthentication
from users_auth.models.models_user import User, LoginHistory, PasswordResetOTP
from users_auth.utils.utils_register import (
    get_tokens_for_user, get_client_ip, send_password_reset_otp_email, generate_otp
)
from users_auth.serializers import ForgotPasswordSerializer, ResetPasswordSerializer, VerifyOTPForgotPasswordSerializer
from datetime import datetime, timedelta
from core.utils import create_notification

class LoginView(APIView):
    """
    API endpoint for user login
    
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        user.last_login_ip = get_client_ip(request)
        user.last_login_device = request.META.get('HTTP_USER_AGENT', '')[:255]
        user.update_last_activity()
        user.save(update_fields=['last_login_ip', 'last_login_device', 'last_activity'])
        
        LoginHistory.objects.create(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
            login_successful=True
        )
        
        tokens = get_tokens_for_user(user)
        
        create_notification(
            user=user,
            title="Login Successful",
            message=f"You have successfully logged in from {get_client_ip(request)}.",
            notification_type="LOGIN_SUCCESSFUL"
        )
        
        user_data = UserSerializer(user).data

        response = Response(
            {
                "message": "Login successful",
            },
            status=status.HTTP_200_OK
        )

        response.set_cookie(
            key="access_token",
            value=tokens["access"],
            httponly=True,
            secure=True,
            samesite="None",
            max_age=60 * 60 * 24 * 30,
        )

        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh"],
            httponly=True,
            secure=True,
            samesite="None",
            max_age=60 * 60 * 24 * 30,
        )

        return response


class LogoutView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        if access_token:
            try:
                token = RefreshToken(access_token)
                token.blacklist()
            except Exception:
                pass

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass

        response = Response(
            {"message": "Logout successful"},
            status=status.HTTP_200_OK
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")  

        response.set_cookie(
            "access_token",
            "",
            max_age=0,
            httponly=True,
            secure=True,
            samesite="None",
            path="/"
        )

        response.set_cookie(
            "refresh_token",
            "",
            max_age=0,
            httponly=True,
            secure=True,
            samesite="None",
            path="/"
        )      

        return response



class ChangePasswordView(APIView):
    """
    API endpoint to change password
    
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.password_changed_at = timezone.now()
        user.save()
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    """
    API endpoint to get and update user profile
    
    """
    serializer_class = UserSerializer
    def get_object(self):   
        return self.request.user
    
    
class AuthCheckView(APIView):
    """
    Check if user is authenticated via HttpOnly cookie

    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.AllowAny]

    def get(self, request):  

        if request.user and request.user.is_authenticated:
            return Response(
                {
                    "isAuthenticated": True,
                    "role": "admin" if request.user.is_admin else "user",
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {"isAuthenticated": False},
            status=status.HTTP_200_OK
        )

class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response(
                {"message": "If an account exists, an OTP has been sent."},
                status=status.HTTP_200_OK
            )

        otp = generate_otp()

        PasswordResetOTP.objects.create(
            user=user,
            otp=otp
        )

        send_password_reset_otp_email(request, user, otp)

        return Response(
            {"message": "OTP sent to your email."},
            status=status.HTTP_200_OK
        )

class VerifyForgotPasswordOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        try:
            user = User.objects.get(email=email)
            otp_obj = PasswordResetOTP.objects.filter(
                user=user,
                otp=otp,
                is_used=False,
                is_verified=False
            ).latest('created_at')
        except (User.DoesNotExist, PasswordResetOTP.DoesNotExist):
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_obj.is_expired():
            return Response(
                {
                    "error": "OTP expired",
                    "can_resend": True
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_obj.is_verified = True
        otp_obj.save(update_fields=["is_verified"])

        return Response(
            {"message": "OTP verified successfully"},
            status=status.HTTP_200_OK
        )

    
class ResendForgotPasswordOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response(
                {"message": "OTP has been sent."},
                status=status.HTTP_200_OK
            )

        # Throttle resend (30 seconds)
        last_otp = PasswordResetOTP.objects.filter(
            user=user
        ).order_by("-created_at").first()

        if last_otp and timezone.now() - last_otp.created_at < timedelta(seconds=30):
            return Response(
                {"error": "Please wait before requesting another OTP"},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Invalidate old OTPs
        PasswordResetOTP.objects.filter(
            user=user,
            is_used=False
        ).update(is_used=True)

        otp = generate_otp()

        PasswordResetOTP.objects.create(
            user=user,
            otp=otp
        )

        send_password_reset_otp_email(request, user, otp)

        return Response(
            {"message": "A new OTP has been sent to your email"},
            status=status.HTTP_200_OK
        )


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(email=email)

            otp_obj = PasswordResetOTP.objects.filter(
                user=user,
                is_verified=True,
                is_used=False
            ).latest('created_at')

        except (User.DoesNotExist, PasswordResetOTP.DoesNotExist):
            return Response(
                {"error": "OTP not verified"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_obj.is_expired():
            return Response(
                {"error": "OTP has expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.password_changed_at = timezone.now()
        user.save()

        otp_obj.is_used = True
        otp_obj.is_verified = False
        otp_obj.save(update_fields=["is_used", "is_verified"])

        return Response(
            {"message": "Password reset successfully"},
            status=status.HTTP_200_OK
        )
