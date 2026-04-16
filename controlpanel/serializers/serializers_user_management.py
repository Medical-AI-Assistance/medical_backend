from rest_framework import serializers
from users_auth.models.models_user import User

class UserManagementSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source='reference_id', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'user_id', 'first_name', 'last_name', 'email', 'username', 
            'is_admin', 'is_active', 'is_banned', 'date_joined'
        ]
        read_only_fields = ['user_id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True, required=False)
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'username', 'phone_number', 'is_admin', 'is_active'
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        from django.db import transaction
        from users_auth.models.models_user import UserProfile
        import logging

        logger = logging.getLogger(__name__)

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    email=validated_data['email'],
                    username=validated_data['username'],
                    password=validated_data['username'],  # create_user automatically hashes the password
                    first_name=validated_data.get('first_name', ''),
                    last_name=validated_data.get('last_name', ''),
                    phone_number=validated_data.get('phone_number', ''),
                    is_admin=validated_data.get('is_admin', False),
                    is_active=validated_data.get('is_active', True)
                )
                try:
                    UserProfile.objects.create(user=user)
                except Exception as exc:
                    logger.error(str(exc), exc_info=True)
                    raise

                return user
        except Exception as exc:
            logger.error(str(exc), exc_info=True)
            raise serializers.ValidationError(f"Failed to create user: {str(exc)}")


class UserStatusSerializer(serializers.Serializer):
    is_banned = serializers.BooleanField(required=True)


class UserAdminSerializer(serializers.Serializer):
    is_admin = serializers.BooleanField(required=True)
