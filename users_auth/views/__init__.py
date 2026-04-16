from .views_login import LoginView, LogoutView, UserProfileView, ChangePasswordView, AuthCheckView, ForgotPasswordView, VerifyForgotPasswordOTPView, ResetPasswordView, ResendForgotPasswordOTPView
from .views_register import RegisterView, VerifyEmailView, ResendVerificationEmailView
from .views_profile import UserProfileDetailView, UserProfileUpdateView, ProfilePictureUpdateAPIView
from .views_notification import NotificationListAPIView, MarkNotificationReadView, MarkAllNotificationsReadView

__all__ = [
    'LoginView',        
    'LogoutView',
    'UserProfileView',
    'ChangePasswordView',
    'RegisterView',
    'VerifyEmailView',
    'ResendVerificationEmailView',
    'AuthCheckView',
    'ForgotPasswordView',
    'VerifyForgotPasswordOTPView',
    'ResetPasswordView',
    'ResendForgotPasswordOTPView',
    'UserProfileDetailView',
    'UserProfileUpdateView',
    'ProfilePictureUpdateAPIView',
    'NotificationListAPIView',
    'MarkNotificationReadView',
    'MarkAllNotificationsReadView',
]