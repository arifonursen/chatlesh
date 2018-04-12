from django.shortcuts import render, reverse, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from ClientModule.models import User, UserFriends


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required(login_url='login')
def IndexView(request):
    template = 'client/index.html'
    friendRequests = UserFriends.objects.filter(friend=request.user, accept=False).order_by('-updated')[:5]
    context = {
        'friendRequests': friendRequests
    }

    return render(request, template, context)


def LoginView(request):
    template = 'client/login.html'
    userIP = get_client_ip(request)
    context = {
        'userIP': userIP
    }

    if request.method == 'POST':
        if request.POST.get('nickName') and request.POST.get('ipAddress'):
            try:
                user = User.objects.get(
                    nick=request.POST.get('nickName'),
                    ip=request.POST.get('ipAddress'),
                )
                if request.FILES.get('avatar'):
                    user.avatar = request.FILES.get('avatar')
                    user.save()
            except:
                user = None
            if user:
                login(request, user)
                return redirect('index')
            else:
                try:
                    createUser = User.objects.create(
                        nick=request.POST.get('nickName'),
                        ip=request.POST.get('ipAddress'),
                        avatar=request.FILES.get('avatar')
                    )
                except:
                    createUser = None
                if createUser:
                    login(request, user)
                    return redirect('index')
                else:
                    context['loginError'] = "Sign in|up error.Please check your information."

    return render(request, template, context)


def LogoutView(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect(reverse('index'))