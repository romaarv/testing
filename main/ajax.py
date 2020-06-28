from django.http import HttpResponse

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
    user_obj=AdvUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)