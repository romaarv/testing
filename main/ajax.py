from django.http import HttpResponse

from .models import *


def check_username_exist(request):
    username=request.POST.get("username")
    user_obj=AdvUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)