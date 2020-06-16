from .models import Lesson, Group

def testing_context_processor(request):
    context = {}
    context['lessons'] = Lesson.objects.filter(is_active=True)
    context['groups'] = Group.objects.filter(is_active=True)
    return context