from rest_framework.serializers import ModelSerializer, ValidationError
from rest_framework import serializers
from authentication.models import User


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['id',
                  'username',
                  'email',
                  'age',
                  'can_be_contacted',
                  'can_data_be_shared']


class UserListSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']


class UserUpdateSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'can_be_contacted', 'can_data_be_shared']


class UserRegisterSerializer(ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username',
                  'email',
                  'password',
                  'password2',
                  'age',
                  'can_be_contacted',
                  'can_data_be_shared']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise ValidationError("Passwords don't match.")
        return data

    def validate_age(self, value):
        if value < 15:
            raise ValidationError("You must be older than 15")
        return value

    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data.
        """
        user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                age=validated_data['age'],
                can_be_contacted=validated_data['can_be_contacted'],
                can_data_be_shared=validated_data['can_data_be_shared'],
                )
        return user


class PasswordUpdateSerializer(ModelSerializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['old_password', 'new_password']
