from ClientModule.models import User

class MyBackend:
    def authenticate(self, request, nick=None, ip=None):
        try:
            user = User.objects.get(nick=nick, ip=ip)
        except:
            user = None

        if user:
            return user
        else:
            return None