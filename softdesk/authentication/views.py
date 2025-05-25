from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render
from django.utils.autoreload import raise_last_exception
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from authentication.models import User
from authentication.serializers import (UserSerializer,
                                        UserUpdateSerializer,
                                        UserRegisterSerializer,
                                        PasswordUpdateSerializer)


class UserCreateView(APIView):
    """
    Allow user registration for anyone
    """

    #TODELETE : for testing purpose
    def get(self, request, *args, **kwargs):
        user = User.objects.all()
        print(request.user)
        serializer = UserSerializer(user, many=True)
        print(serializer.data)
        #if serializer.is_valid():
        return Response(serializer.data)
        #return Response("prout", status=status.HTTP_226_IM_USED)

    def post(self, request):
        """
        User subscription
        Args:
        """
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response = {
                "message": "User created successfully",
                "data": serializer.data
            }
            return Response(data=response,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


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
            return Response(serializer.errors,
                            status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        user = request.user
        print("coucou", request.data['user'])
        serializer = UserUpdateSerializer(user, data=request.data)
        print(serializer.initial_data)
        if serializer.is_valid():
            serializer.save()
            return Response("Data updated",
                            status=status.HTTP_201_CREATED)
        return Response("Error",
                        status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        username = request.user.username
        if 'user' in request.data:
            if username == request.data['user']:
                user.delete()
                return Response(f"User {username} deleted.",
                                status=status.HTTP_204_NO_CONTENT)
            return Response("Token's owner and user provided don't match",
                            status=status.HTTP_400_BAD_REQUEST)
        return Response("Username to delete must be given in data",
                        status=status.HTTP_400_BAD_REQUEST)




