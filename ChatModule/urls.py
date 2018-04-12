"""Bitirme URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from .views import (ChatConnect, onlineUsers, FriendOrChatRequest, CheckFriendRequests,
                    FriendRequestAccept, AcceptRequest, OpenChatPanel)

urlpatterns = [
    path('connect/', ChatConnect, name='connectChat'),
    path('onlineUsers/', onlineUsers, name='onlineUsers'),
    path('friendOrChatRequest/', FriendOrChatRequest, name='friendOrChatRequest'),
    path('checkFriendRequests/', CheckFriendRequests, name='checkFriendRequests'),
    path('friendRequestAccept/', FriendRequestAccept, name='friendRequestAccept'),
    path('acceptRequest/', AcceptRequest, name='acceptRequest'),
    path('openChatPanel/<str:key>/', OpenChatPanel, name='openChatPanel'),
]
