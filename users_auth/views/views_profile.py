from users_auth.models.models_user import User
from users_auth.serializers import UserSerializer
from core.authentication import CookieJWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core import permissions
from rest_framework.parsers import MultiPartParser, FormParser
from users_auth.serializers.serializers_user import ProfilePictureSerializer


class UserProfileDetailView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request},)
        return Response({
            "message": "Profile fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    
class UserProfileUpdateView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            context={'request': request},
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfilePictureUpdateAPIView(APIView):
    """
    Dedicated endpoint for updating or removing the user's profile picture using multipart/form-data.
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request):
        profile = request.user.profile
        serializer = ProfilePictureSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            
            # Recalculate percentage
            profile.calculate_completion_percentage()

            return Response({
                "message": "Profile picture updated successfully",
                "profile_picture": request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
        profile = request.user.profile
        if profile.profile_picture:
            profile.profile_picture.delete()
            profile.save()
            profile.calculate_completion_percentage()
            
        return Response({"message": "Profile picture removed successfully"}, status=status.HTTP_200_OK)