from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import date as _date

from ClientModule.models import User


class Thread(models.Model):
    key = models.CharField(max_length=254, editable=False, unique=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    lastMessage = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return self.key


class Message(models.Model):
    text = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    read = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return str(self.sender.id)

    @property
    def formatted_timestamp(self):
        return _date(self.datetime, 'd F Y H:i')

    def as_dict(self):
        return {'sender': self.sender.nick, 'id': self.sender.id, 'text': self.text, 'datetime': self.formatted_timestamp,
                'read': self.read}


def update_last_message_datetime(sender, instance, created, **kwargs):
    if not created:
        return

    Thread.objects.filter(id=instance.thread.id).update(
        lastMessage=instance.datetime
    )


post_save.connect(update_last_message_datetime, sender=Message)