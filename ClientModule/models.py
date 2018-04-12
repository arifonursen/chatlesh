from django.db import models
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import PermissionsMixin
from django.utils.crypto import salted_hmac

from .managers import UserManager


class User(PermissionsMixin):
    nick = models.CharField(verbose_name='Nickname', max_length=20, unique=True)
    ip = models.CharField(max_length=20, verbose_name='IP', unique=True)
    password = models.CharField(verbose_name='Şifre', null=True, blank=True, max_length=128)
    date_joined = models.DateTimeField(verbose_name='Kayıt Tarihi', auto_now_add=True)
    is_active = models.BooleanField('Aktif mi ?', default=True)
    is_staff = models.BooleanField(verbose_name='Yetkili mi ?', default=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'nick'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Kullanıcılar'
        verbose_name_plural = 'Kullanıcılar'

    def __str__(self):
        return self.nick

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        def setter(raw_password):
            self.set_password(raw_password)
            self._password = None
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter)

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    def get_session_auth_hash(self):
        key_salt = "django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash"
        return salted_hmac(key_salt, self.password).hexdigest()


class UserFriends(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend')
    accept = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.nick