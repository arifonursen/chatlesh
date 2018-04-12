import json
import logging
from channels import Group
from channels.auth import channel_session_user
from channels.sessions import channel_session
from django.forms.models import model_to_dict
from .models import Thread
from ChatModule.models import User
from datetime import datetime
import hashlib, random

log = logging.getLogger(__name__)
usersArr = []

@channel_session
def ws_connect(message):
    try:
        th = Thread.objects.get(key=message['path'].split('/')[3])
    except:
        th = None
    if th:
        Group('chat-' + str(th.key)).add(message.reply_channel)
        message.channel_session['room'] = th.key
    else:
        Group('chat-global').add(message.reply_channel)
    message.reply_channel.send({"accept": True})


@channel_session
def ws_receive(message):
    key = message.channel_session['room']
    data = json.loads(message['text'])
    if data['sender'] and data['text'] is not None:
        th = Thread.objects.get(key=key)
        th.lastMessage = datetime.now()
        user = User.objects.get(id=data['sender'])
        th.messages.create(text=data['text'], sender=user)
        m = {
            'sender': user.nick,
            'dateTime': datetime.now().strftime('%-d %b %-H:%M'),
            'text': data['text']
        }
        Group('chat-' + str(key)).send({'text': json.dumps(m)})


@channel_session
def ws_disconnect(message):
    try:
        roomSession = message.channel_session['room']
    except:
        roomSession = None
    if roomSession:
        Group('chat-' + str(message.channel_session['room'])).discard(message.reply_channel)
    else:
        Group('chat-global').discard(message.reply_channel)