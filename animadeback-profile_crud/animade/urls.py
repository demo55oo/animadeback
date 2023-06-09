"""
URL configuration for animade project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from knox import views as knox_views
from .views import *
from django.urls import path , re_path
from django.views.generic.base import TemplateView
# Serializers define the API representation.


# Routers provide an easy way of automatically determining the URL conf.

urlpatterns = [ 
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/login/', LoginAPI.as_view(), name='login'),
    path('api/logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('api/logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    path('api/auth/user/', MainUser.as_view()),
    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('api/profile/self/', MyProfileAPIView.as_view(), name = 'myprofile'),
    path('api/profile/create/', CreateProfileAPIView.as_view(), name = 'createprofile'),
    path('api/user/<user_id>/profile/', ProfileAPIView.as_view(), name = 'profile'),
    path('api/user/<user_id>/profile/modify/', ProfileModifyAPIView.as_view(), name = 'profilemodify'),
    path('api/createddesign/', CreatedDesignAPIView.as_view(), name = 'createddesign'),
    path('api/createddesign/<int:pk>/', CreatedDesignRetrieveView.as_view(), name = 'createddesign'),
    path('api/createddesign/<int:pk>/update/', CreatedDesignUpdateView.as_view(), name = 'createddesignupdate'),
    path('api/createddesign/<int:pk>/delete/', CreatedDesignDestroyView.as_view(), name = 'createddesigndelete'),
    path('api/createddesign/<int:pk>/save/', SaveDesignAPIView.as_view(), name = 'savedesign'),
    path('api/createddesign/<int:pk>/unsave/', UnsaveDesignAPIView.as_view(), name = 'unsavedesign'),
    path('api/user/saveddesign/', UserSavedDesignAPIView.as_view(), name = 'saveddesign'),
    path('send_email/', send_email, name = 'sendemail'),


    # path('api/saveddesign/<int:pk>/', SavedDesignRUDView.as_view()),

]