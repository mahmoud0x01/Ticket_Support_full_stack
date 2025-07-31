from rest_framework import serializers
from .models import User, UserProfile, SupportProfile
from django.contrib.auth.password_validation import validate_password


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['tickets_submitted']


class SupportProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportProfile
        fields = ['tickets_assigned', 'tickets_resolved']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    support_profile = SupportProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'age', 'user_type', 'password', 'confirm_password',
                  'profile', 'support_profile']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            age=validated_data.get('age'),
            user_type=validated_data.get('user_type', 'user')
        )

        if user.user_type == 'user':
            UserProfile.objects.create(user=user)
        elif user.user_type == 'support':
            SupportProfile.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
