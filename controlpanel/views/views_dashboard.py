from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from core import permissions
from core.authentication import CookieJWTAuthentication

from users_auth.models.models_user import User
import logging

logger = logging.getLogger(__name__)

class AdminAccessibleAPIView(APIView):
    """
    Base APIView specifying admin access requirements
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAdminUser]

class DashboardStatsAPIView(AdminAccessibleAPIView):
    """
    API endpoint to fetch dashboard statistics.
    """
    def get(self, request):
        total_users = User.objects.count()
        total_active_users = User.objects.filter(is_active=True).count()
        total_banned_users = User.objects.filter(is_banned=True).count()
        total_admin_users = User.objects.filter(is_admin=True).count()

        data = {
            "total_users": total_users,
            "total_active_users": total_active_users,
            "total_banned_users": total_banned_users,
            "total_admin_users": total_admin_users,
        }

        return Response({
            "message": "Dashboard statistics fetched successfully",
            "data": data
        }, status=status.HTTP_200_OK)
