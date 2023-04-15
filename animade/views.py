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
from rest_framework.parsers import MultiPartParser

from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView

from django.contrib.auth import login
from django.contrib.auth.models import User

from .models import Profile, CreatedDesign, SavedDesign
from .serializers import UserSerializer, RegisterSerializer, ChangePasswordSerializer,ProfileSerializer, CreatedDesignSerializer, SavedDesignSerializer
from .permissions import OwnerPermission


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
  serializer_class = UserSerializer

  def get_object(self):
    return self.request.user

class CreateProfileAPIView(APIView):
    """
        View to Create User profile if it doesn't already exists
    """
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
    """
        View to see profile info
    """
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request, *args, **kwargs):
        profile = Profile.objects.get(user__id=kwargs['user_id'])
        profile_serializer = ProfileSerializer(profile)
        return Response(profile_serializer.data)

class MyProfileAPIView(APIView):
    """
        View to see profile info
    """
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request, *args, **kwargs):
        profile = Profile.objects.get(user=request.user)
        profile_serializer = ProfileSerializer(profile)
        return Response(profile_serializer.data)

class ProfileModifyAPIView(APIView):
    """
        View to update and delete profile
    """

    permission_classes = [
        permissions.IsAuthenticated, OwnerPermission
    ]

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
    """
        View to create and list CreatedDesign
    """
    permission_classes = [
        permissions.IsAuthenticated, OwnerPermission
    ]

    parser_classes = (MultiPartParser,)

    def get(self, request, *args, **kwargs):
        profile = CreatedDesign.objects.all()
        design_serializer = CreatedDesignSerializer(profile, many = True)
        print(profile)
        return Response(design_serializer.data)
    
    def post(self, request, *args, **kwargs):
        design_data = request.POST.dict()
        file_obj = request.FILES['image']
        design_data['image'] = request.FILES['image']
        print(design_data)
        serializer = CreatedDesignSerializer(data = design_data)
        # return Response(status=status.HTTP_201_CREATED)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Design Created Successfully"},status=status.HTTP_201_CREATED)
        return Response({"message":"Could not Create Design"},status=status.HTTP_304_NOT_MODIFIED)

class CreatedDesignRetrieveView(generics.RetrieveAPIView):
    """
        Created Design Detail View
    """
    permission_classes = [
        permissions.IsAuthenticated
    ]
    queryset = CreatedDesign.objects.all()
    serializer_class = CreatedDesignSerializer


class CreatedDesignUpdateView(generics.UpdateAPIView):
    """
        Created Design Update View
    """
    permission_classes = [
        permissions.IsAuthenticated, permissions.IsAdminUser
    ]
    queryset = CreatedDesign.objects.all()
    serializer_class = CreatedDesignSerializer


class CreatedDesignDestroyView(generics.DestroyAPIView):
    """
        Created Design Delete View
    """
    permission_classes = [
        permissions.IsAuthenticated, permissions.IsAdminUser
    ]
    queryset = CreatedDesign.objects.all()
    serializer_class = CreatedDesignSerializer

class SaveDesignAPIView(APIView):
    """
        View to save design
    """
    permission_classes = [
        permissions.IsAuthenticated
    ]
    def get(self, request, *args, **kwargs):
        user = request.user
        design = CreatedDesign.objects.get(id = kwargs['pk'])
        try:
            saveddesign = get_object_or_404(SavedDesign, design = design)
            print(saveddesign)
            print(type(saveddesign), saveddesign)
            saveddesign.status = True
            saveddesign.save()
            return Response({"message" :"Design saved successfully!"},status=status.HTTP_201_CREATED)
        
        except:
            SavedDesign.objects.create(user = user, design = design, status = True)
            return Response({"message" :"Design saved successfully!"},status=status.HTTP_201_CREATED)

class UnsaveDesignAPIView(APIView):
    """
        View to save design
    """
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request, *args, **kwargs):
        try:
            design = SavedDesign.objects.get(design__id = kwargs['pk'],user = request.user)
        except:
            return Response({"message": "Design not found saved"}, status = 404)
        design.status = False
        design.save()
        # User.objects.create(user = user, design = design, status = True)
        return Response({"message" :"Design Unsaved successfully!"},status=status.HTTP_201_CREATED)

class UserSavedDesignAPIView(APIView):
    """
        View to list saved designs of requesting user
    """
    permission_classes = [  
        permissions.IsAuthenticated
    ]

    def get(self, request, *args, **kwargs):
        design = SavedDesign.objects.filter(user = request.user, status = True)
        design_serializer = SavedDesignSerializer(design, many = True)
        return Response(design_serializer.data)

# class SavedDesignRUDView(generics.RetrieveUpdateDestroyAPIView):
#     """
#         Saved Design Detail, Update and Delete View
#     """
#     permission_classes = [
#         permissions.IsAuthenticated, OwnerPermission
#     ]
#     queryset = SavedDesign.objects.all()
#     serializer_class = SavedDesignSerializer