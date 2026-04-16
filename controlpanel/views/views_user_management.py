from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Q

from core import permissions
from core.authentication import CookieJWTAuthentication

from users_auth.models.models_user import User, UserProfile
from controlpanel.serializers import (
    UserManagementSerializer,
    UserCreateSerializer,
    UserStatusSerializer,
    UserAdminSerializer
)
import logging

logger = logging.getLogger(__name__)

class AdminAccessibleAPIView(APIView):
    """
    Base APIView specifying admin access requirements
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAdminUser]


class UserListAPIView(AdminAccessibleAPIView):
    """
    API endpoint to list all users, with optional search filtering by email or name.
    """
    def get(self, request):
        search_query = request.query_params.get('search', '')
        users = User.objects.all().order_by('-date_joined')
        
        if search_query:
            users = users.filter(
                Q(email__icontains=search_query) | 
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query) |
                Q(username__icontains=search_query)
            )

        serializer = UserManagementSerializer(users, many=True)
        return Response({
            "message": "Users fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class UserCreateAPIView(AdminAccessibleAPIView):
    """
    API endpoint for admin to create a new user. The password assumes the username.
    """
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response({
                "message": "User created successfully",
                "data": UserManagementSerializer(user).data
            }, status=status.HTTP_201_CREATED)


class UserBanAPIView(AdminAccessibleAPIView):
    """
    API endpoint to ban or unban a user.
    """
    def post(self, request, reference_id):
        
        if 'is_banned' not in request.data:
            return Response({"message": "is_banned is required"}, status=status.HTTP_400_BAD_REQUEST) 

        request_action = request.data.get('is_banned')            

        try:
            user = User.objects.get(reference_id=reference_id)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if request_action == user.is_banned:
            return Response({"message": "User is already " + ("banned" if request_action else "unbanned")}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent admin from banning themselves 
        if user == request.user:
            return Response({"error": "You cannot " + ("ban" if request_action else "unban") + " yourself."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserStatusSerializer(data=request.data)
        if serializer.is_valid():
            is_banned = serializer.validated_data['is_banned']
            
            user.is_banned = is_banned
            
            # If a user is banned, also disable them from active sessions
            if is_banned:
                user.is_active = False
            else:
                user.is_active = True
                
            user.save(update_fields=['is_banned', 'is_active'])

            action_text = "banned" if is_banned else "unbanned"
            return Response({
                "message": f"User {action_text} successfully.",
                "data": UserManagementSerializer(user).data
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "User status update failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserAdminRightsAPIView(AdminAccessibleAPIView):
    """
    API endpoint to grant or revoke admin rights.
    """
    def post(self, request, reference_id):

        if 'is_admin' not in request.data:
            return Response({"message": "is_admin is required"}, status=status.HTTP_400_BAD_REQUEST) 

        request_action = request.data.get('is_admin')

        try:
            user = User.objects.get(reference_id=reference_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


        if request_action == user.is_admin:
            return Response({"message": "User is already " + ("admin" if request_action else "not admin")}, status=status.HTTP_400_BAD_REQUEST)
        

        # Prevent admin from removing their own admin rights blindly, optional but good practice
        if user == request.user and not request.data.get('is_admin', True):
            return Response({"error": "You cannot remove your own admin rights."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserAdminSerializer(data=request.data)
        if serializer.is_valid():
            is_admin = serializer.validated_data['is_admin']
            
            user.is_admin = is_admin
            user.is_staff = is_admin # Need to sync this because Django uses is_staff for general admin access historically
            user.save(update_fields=['is_admin', 'is_staff'])

            action_text = "granted" if is_admin else "revoked"
            return Response({
                "message": f"Admin rights {action_text} successfully.",
                "data": UserManagementSerializer(user).data
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "Admin rights update failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
