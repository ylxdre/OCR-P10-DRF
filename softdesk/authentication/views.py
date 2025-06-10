from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render
from django.utils.autoreload import raise_last_exception
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied

from authentication.models import User
from authentication.serializers import (UserSerializer,
                                        UserUpdateSerializer,
                                        UserRegisterSerializer,
                                        PasswordUpdateSerializer)


class UserCreateView(APIView):
    """
    Allow user registration for anyone
    """
    def post(self, request):
        """
        Creates a new user
        Requires :
        username->str, email->str, password->str, password2->str, age->int,
        can_be_contacted->bool, can_data_be_shared->bool
        """
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response = {
                "detail": "User created successfully",
                "data": serializer.data
            }
            return Response(data=response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = PasswordUpdateSerializer(data=request.data)
        if serializer.is_valid():
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password":"Wrong password"},
                                status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get('new_password'))
            user.save()
            update_session_auth_hash(request, user)
            response = {
                "detail": "Password updated successfully."
            }
            return Response(response, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "detail": "Data updated",
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
        response = {"detail": "Data error"}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        username = request.user.username
        if 'user' in request.data:
            if username == request.data['user']:
                user.delete()
                response = {"detail": f"User {username} deleted."}
                return Response(response, status=status.HTTP_204_NO_CONTENT)
            raise PermissionDenied()
        response = {"detail": "Username to delete must be given in data"}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

