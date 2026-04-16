from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.authentication import CookieJWTAuthentication
from users_auth.models.models_notification import Notification
from users_auth.serializers.serializers_notification import NotificationSerializer

class NotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

class MarkNotificationReadView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, reference_id):
        try:
            notification = Notification.objects.get(reference_id=reference_id, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

class MarkAllNotificationsReadView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        updated_count = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response(
            {'message': f'Successfully marked {updated_count} notifications as read.'}, 
            status=status.HTTP_200_OK
        )