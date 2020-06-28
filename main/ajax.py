from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType

from .models import *


def ajax_required(f):
   def wrap(request, *args, **kwargs):
       if not request.is_ajax():
           return HttpResponseBadRequest()
       return f(request, *args, **kwargs)
   wrap.__doc__=f.__doc__
   wrap.__name__=f.__name__
   return wrap


@ajax_required
def check_username_exist(request):
    username=request.POST.get("username")
    login_user = AdvUser.objects.filter(username=username)
    if login_user.exists():
        if login_user.filter(is_active=True).exists():
            return HttpResponse(1) # Логин активирован
        else:
            if LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(AdvUser),
                                        object_id=str(login_user[0].id))[:1].exists():
                return HttpResponse(3) # Логин отключен администратором
            else:
                return HttpResponse(2) # Логин не активирован пользователем
    else:
        return HttpResponse(0) # Логин не существует