import math, random

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, throttle_classes,permission_classes

from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView

from django.contrib.auth import login
from django.contrib.auth.models import User

from .models import Profile, CreatedDesign, SavedDesign
from .serializers import UserSerializer, RegisterSerializer, ChangePasswordSerializer,ProfileSerializer, CreatedDesignSerializer, SavedDesignSerializer
from .permissions import ProfileOwnerPermission

class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
        "user": UserSerializer(user, context=self.get_serializer_context()).data,
        "token": AuthToken.objects.create(user)[1]
        })


class LoginAPI(KnoxLoginView):
        permission_classes = (permissions.AllowAny,)

        def post(self, request, format=None):
            serializer = AuthTokenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            login(request, user)
            return super(LoginAPI, self).post(request, format=None)


class MainUser(generics.RetrieveAPIView):
  permission_classes = [
      permissions.IsAuthenticated
  ]
  serializer_class = UserSerializer()

  def get_object(self):

    return self.request.user

class CreateProfileAPIView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        if not user.profile:
            Profile.objects.create(user = user)
            return Response(status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_304_NOT_MODIFIED)

class ProfileAPIView(APIView):
    permission_classes = [
        permissions.IsAuthenticated, ProfileOwnerPermission
    ]

    def get(self, request, *args, **kwargs):
        profile = Profile.objects.get(user__id=kwargs['user_id'])
        profile_serializer = ProfileSerializer(profile)
        return Response(profile_serializer.data)

    def put(self, request, *args, **kwargs):
        profile = Profile.objects.get(user__id=kwargs['user_id'])
        self.check_object_permissions(self.request, profile)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        profile = Profile.objects.get(user__id=kwargs['user_id'])
        self.check_object_permissions(self.request, profile)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CreatedDesignAPIView(APIView):
    permission_classes = [
        permissions.IsAuthenticated, ProfileOwnerPermission
    ]

    def get(self, request, *args, **kwargs):
        profile = CreatedDesign.objects.get(user__id=kwargs['user_id'])
        design_serializer = CreatedDesignSerializer(profile)
        return Response(design_serializer.data)

class SavedDesignAPIView(APIView):
    permission_classes = [
        permissions.IsAuthenticated, ProfileOwnerPermission
    ]

    def get(self, request, *args, **kwargs):
        profile = SavedDesign.objects.get(user__id=kwargs['user_id'])
        design_serializer = SavedDesignSerializer(profile)
        return Response(design_serializer.data)
