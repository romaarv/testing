from .models import Lesson

def testing_context_processor(request):
    context = {}
    context['lessons'] = Lesson.objects.all()
    return context