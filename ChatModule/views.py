from django.forms.models import model_to_dict
from django.db.models.aggregates import Q
from django.shortcuts import render
from django.http.response import HttpResponse

from rest_framework.views import APIView

from .models import Thread
from ClientModule.models import User, UserFriends

import json, hashlib

onlineUserArr = []


def ChatConnect(request):
    return True


def onlineUsers(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(nick=request.POST.get('nick'),
                                    ip=request.POST.get('ip'))
        except:
            user = None

        if user:
            modelUser = {
                'userNickName': user.nick,
                'userIP': user.ip,
                'userAvatar': user.avatar.url
            }
            if modelUser not in onlineUserArr and request.POST.get('type') == 'onOpen':
                onlineUserArr.append(modelUser)
            elif modelUser in onlineUserArr and request.POST.get('type') == 'onClose':
                onlineUserArr.remove(modelUser)
            return HttpResponse(json.dumps(onlineUserArr), content_type='application/json; charset=utf-8')


def FriendOrChatRequest(request):
    if request.method == 'POST' and request.user.nick != request.POST.get('usernickName'):
        friend = User.objects.get(nick=request.POST.get('usernickName'))
        isUserRequestExist = UserFriends.objects.filter(user=request.user, friend=friend, accept=False)
        if isUserRequestExist:
            template = 'client/friendshipRequestModal.html'
            context = {'friend': friend, 'isWaiting': True}
            return render(request, template, context)
        else:
            canChatStart = UserFriends.objects.filter(Q(user=request.user, friend=friend) |
                                                      Q(user=friend, friend=request.user), accept=True)
            if canChatStart:
                couples = canChatStart.first()
                hashedKey = hashlib.sha256(str(couples.timestamp).encode('utf-8')).hexdigest()
                try:
                    thread = Thread.objects.get(key=hashedKey)
                except:
                    thread = Thread.objects.create(key=hashedKey, sender=request.user, receiver=friend)
                if thread:
                    return HttpResponse(json.dumps({'msg': 'openChat', 'threadID': thread.key}),
                                        content_type='application/json; charset=utf-8')
            else:
                isFriendRequest = UserFriends.objects.filter(user=friend, friend=request.user, accept=False)
                if isFriendRequest:
                    template = 'client/friendRequestAcceptModal.html'
                    context = {'friendRequest': isFriendRequest}
                    return render(request, template, context)
                else:
                    template = 'client/friendshipRequestModal.html'
                    createRequest = UserFriends.objects.create(user=request.user, friend=friend)
                    context = {'friend': friend}
                    return render(request, template, context)


def FriendRequestAccept(request):
    if request.method == 'POST' and request.user.is_authenticated:
        template = 'client/friendRequestAcceptModal.html'
        try:
            friendRequest = UserFriends.objects.get(id=int(request.POST.get('requestID')), accept=False)
        except:
            friendRequest = None

        if friendRequest:
            context = {'friendRequest': friendRequest}
            return render(request, template, context)


def AcceptRequest(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            accept = UserFriends.objects.get(id=int(request.POST.get('requestID')), accept=False)
            accept.accept = True
            accept.save()
        except:
            accept = None

        if accept:
            return HttpResponse(json.dumps({'msg': 'success'}), content_type='application/json; charset=utf-8')


def CheckFriendRequests(request):
    if request.method == 'POST' and request.user.is_authenticated:
        friendRequests = UserFriends.objects.filter(friend=request.user, accept=False).order_by('-updated')[:5]
        totalRequests = []
        for friend in friendRequests:
            totalRequests.append({
                'requestID': friend.id,
                'friendNick': friend.user.nick,
                'friendAvatar': friend.user.avatar.url
            })
        return HttpResponse(json.dumps(totalRequests), content_type='application/json; chatset=utf-8')


def OpenChatPanel(request, key):
    try:
        thread = Thread.objects.get(key=key)
    except:
        thread = None
    if thread:
        if request.user == thread.sender or request.user == thread.receiver:
            template = 'chat/chatPanel.html'
            if thread.sender != request.user:
                receiver = thread.sender
            else:
                receiver = thread.receiver
            context = {'thread': thread, 'receiver': receiver, 'messages': reversed(thread.messages.order_by('-datetime'))}
            return render(request, template, context)