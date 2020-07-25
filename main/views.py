from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.core.paginator import Paginator
from django.core.signing import BadSignature
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.views.generic import ListView
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Max, Sum #Q, OuterRef, Subquery
import random

from .models import *
from .forms import ChangeUserInfoForm, RegisterUserForm
from .utilities import signer


def other_page(request, page):
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


def index(request):
    context = {}
    count_limit = 10 # Количество последних тестов для отображения на странице
    context['count_limit'] = count_limit
    content_type = ContentType.objects.get_for_model(Task)
    # last_tests = Task.objects.filter(is_active=True).annotate(modified_at=Subquery(
    #     LogEntry.objects.filter(content_type_id=content_type.id, object_id=str(OuterRef('id')),).order_by(
    #   '-action_time').values('action_time')[:1]
    # )).order_by('-modified_at')[:count_limit]
    # print(last_tests.query)
    last_tests = Task.objects.raw("\
            SELECT task.id, task.lesson_id, task.name, task.content, task.max_score, MAX (log.action_time) AS modified_at\
            FROM main_task task, django_admin_log log\
            WHERE task.is_active=True AND log.content_type_id=%d AND task.id=CAST(log.object_id AS INTEGER)\
            GROUP BY task.id, log.object_id ORDER BY modified_at DESC LIMIT %d\
        " % (content_type.id, count_limit)
    )
    for test in last_tests:
        str1 = ''
        test.group_in = str1
        max_len = len(test.groups.filter(is_active=True))
        count = 0
        for group in test.groups.filter(is_active=True):
            count += 1
            if count == 1:
                str1 = group.name
            else:
                str1 += ', ' + group.name
        if max_len > 0:
            str1 += '.'
        test.group_in = str1
    context['tests'] = last_tests
    return render(request, 'main/index.html', context)


class TestingLoginView(LoginView):
    template_name = 'main/login.html'


class TestingLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'main/logout.html'


@login_required
def profile(request):
    tests = Test.objects.filter(user=request.user.id)
    for test in tests:
        str = ''
        test.group_in = str
        max_len = len(test.task.groups.filter(is_active=True))
        count = 0
        for group in test.task.groups.filter(is_active=True):
            count += 1
            if count == 1:
                str = group.name
            else:
                str += ', ' + group.name
        if max_len > 0:
            str += '.'
        test.group_in = str
        date_ = Exam.objects.filter(answer__question__test=test.task_id).order_by('id').first()
        test.start_at = date_.date_at
        date_ = Exam.objects.filter(answer__question__test=test.task_id).order_by('id').last()
        test.end_at = date_.date_at
    context = {}
    paginator = Paginator(tests, 20)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context['page'] = page
    page = paginator.get_page(page_num)
    context['tests'] = page.object_list
    return render(request, 'main/profile.html', context)


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'main/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('main:profile')
    success_message = 'Личные данные пользователя изменены'

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class TestingPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Пароль пользователя изменен'


class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main:register_done')


class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)
    context = {'user_new': user}
    if user.is_activated:
        template = 'main/user_is_activated.html'
    else:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template, context)


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удален')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class TaskByLessonView (ListView):
    context_object_name = 'tasks'
    paginate_by = 20

    def get_queryset (self):
        qs = Task.objects.filter(is_active=True, lesson=self.kwargs['lesson_id'])
        for test in qs:
            str = ''
            test.group_in = str
            max_len = len(test.groups.filter(is_active=True))
            count = 0
            for group in test.groups.filter(is_active=True):
                count += 1
                if count == 1:
                    str = group.name
                else:
                    str += ', ' + group.name
            if max_len > 0:
                str += '.'
            test.group_in = str
            str = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(Task),
                object_id=test.id).order_by('-action_time')[:1]
            if len(str) > 0:
                test.modified_at = str[0].action_time
            else:
                test.modified_at = None
        return qs

    def get_context_data (self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['current_lesson'] = Lesson.objects.get(pk=self.kwargs['lesson_id'])
        return context


class TaskByGroupView (ListView):
    context_object_name = 'tasks'
    template_name = 'main/task_for_group_list.html'
    paginate_by = 20

    def get_queryset (self):
        qs = Task.objects.filter(is_active=True, groups=self.kwargs['group_id'])
        for test in qs:
            str = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(Task),
                object_id=test.id).order_by('-action_time')[:1]
            if len(str) > 0:
                test.modified_at = str[0].action_time
            else:
                test.modified_at = None
        return qs

    def get_context_data (self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['current_group'] = Group.objects.get(pk=self.kwargs['group_id'])
        return context


class SearchResultView (ListView):
    model = Task
    template_name = 'main/search_results.html'
    paginate_by = 20

    def get_context_data (self, *args, **kwargs):
        context = {}
        context = super().get_context_data(*args, **kwargs)
        context['last_question'] = '?search_text=%s' % self.request.GET.get('search_text', '')
        context['search_text'] = self.request.GET.get('search_text', '')
        return context

    def get_queryset (self):
        sh = self.request.GET.get('search_text', '')
        qs = Task.objects.filter(Q(lesson__name__icontains=sh) | Q(groups__name__icontains=sh) |
                Q(max_score__icontains=sh) | Q(content__icontains=sh)).filter(is_active=True).distinct()
        for test in qs:
            str = ''
            test.group_in = str
            max_len = len(test.groups.filter(is_active=True))
            count = 0
            for group in test.groups.filter(is_active=True):
                count += 1
                if count == 1:
                    str = group.name
                else:
                    str += ', ' + group.name
            if max_len > 0:
                str += '.'
            test.group_in = str
            str = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(Task),
                object_id=test.id).order_by('-action_time')[:1]
            if len(str) > 0:
                test.modified_at = str[0].action_time
            else:
                test.modified_at = None
        return qs


@login_required
def start_testing(request, task_id):
    if request.user.is_staff:
        return render(request, 'main/start_testing.html', None)
    task = get_object_or_404(Task, id=task_id)
    str = ''
    task.group_in = str
    max_len = len(task.groups.filter(is_active=True))
    count = 0
    for group in task.groups.filter(is_active=True):
        count += 1
        if count == 1:
            str = group.name
        else:
            str += ', ' + group.name
    if max_len > 0:
        str += '.'
    task.group_in = str
    context = {'task': task}
    context['is_pass'] = False
    if Test.objects.filter(user=request.user.id, task=task_id).exists():
        context['is_pass'] = True
    return render(request, 'main/start_testing.html', context)


@login_required
@require_POST
def testing(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    str_ = ''
    task.group_in = str_
    max_len = len(task.groups.filter(is_active=True))
    count = 0
    for group in task.groups.filter(is_active=True):
        count += 1
        if count == 1:
            str_ = group.name
        else:
            str_ += ', ' + group.name
    if max_len > 0:
        str_ += '.'
    task.group_in = str_
    context = {'task': task}
    if (len(request.POST.getlist('answer_user'))) > 0:
        for answer_user in request.POST.getlist('answer_user'):
            answer_ = Exam(user=AdvUser(id=request.user.id), answer=Answer(id=answer_user))
            answer_.save()
    exam = Exam.objects.filter(user=request.user.id, answer__question__test=task_id)
    if exam.exists():
        v = exam.first()
        variant = v.answer.question.variant
        v = Question.objects.filter(test=task_id, variant=variant, is_active=True).count()
        questions = Question.objects.raw("\
            SELECT DISTINCT question.id, question.content\
            FROM main_question question, main_answer answer\
            WHERE question.test_id=%d and question.variant=%d and question.is_active=True and answer.is_active=True\
                and question.id=answer.question_id AND question.id not IN\
            (SELECT DISTINCT answer.question_id FROM main_exam exam, main_answer answer WHERE exam.answer_id=answer.id)\
            ORDER BY question.id" % (task_id, variant)
        )
        question_of = v - len(questions) + 1
        if question_of > v:
            questions = Question.objects.filter(test=task_id, variant=variant, is_active=True)
            max_score = questions[0].test.max_score # МАХ оценка за тест
            questions = Question.objects.filter(test=task_id, variant=variant, 
                is_active=True).aggregate(max_score_of_questions=Sum('score'))
            max_score_of_questions = questions['max_score_of_questions'] # MAX количество балов в тесте
            score_of_questions = 0 # Набранное количество балов
            questions = Question.objects.raw("\
                SELECT question.id, question.score FROM main_answer answer, main_exam exam, main_question question\
                WHERE question.test_id=%d AND question.variant=%d AND question.is_active=True AND answer.question_id=question.id\
                    AND question.type_answer=FALSE AND answer.is_true=True AND answer.id=exam.answer_id\
                GROUP BY question.id" % (task_id, variant)
            )
            for question in questions:
                score_of_questions += question.score
            questions = Question.objects.raw("\
                SELECT question.id, COUNT(answer.id) as asks_is_true, question.score\
                FROM main_question question, main_answer answer\
                    RIGHT JOIN main_exam exam ON answer.id=exam.answer_id\
                WHERE question.test_id=%d AND question.variant=%d AND question.is_active=True and question.type_answer=TRUE\
                    AND answer.question_id=question.id AND (question.type_answer=True AND answer.is_true=TRUE)\
                    AND question.id NOT IN\
                (SELECT question.id FROM main_question question, main_answer answer, main_exam exam\
                WHERE question.test_id=%d AND question.variant=%d AND question.is_active=True AND answer.question_id=question.id\
                AND answer.id=exam.answer_id AND (question.type_answer=TRUE AND answer.is_true=FALSE))\
                GROUP BY question.id\
                " % (task_id, variant, task_id, variant)
            )
            for question in questions:
                if question.asks_is_true == Answer.objects.filter(question__test=task_id, question=question.id,
                                            question__variant=variant, is_active=True, is_true=True).count():
                    score_of_questions += question.score
            test_score = score_of_questions * max_score / max_score_of_questions # Оценка за тест
            test_ = Test(task=Task(id=task_id) ,user=AdvUser(id=request.user.id), test_score=test_score)
            test_.save()
            return redirect(reverse_lazy('main:profile'))
        else:
            context['question_of'] = str(question_of) + ' из ' + str(v) + '.'
            context['question'] = questions[0]
            answers = Answer.objects.filter(question=questions[0], is_active=True).order_by('id')
            context['answers'] = answers
    else:
        question = Question.objects.filter(test=task_id, is_active=True).order_by('-variant')[0]
        variant = random.randint(1, question.variant)
        question = Question.objects.filter(test=task_id, variant=variant, is_active=True).order_by('id').count()
        context['question_of'] = '1 из '+str(question)+'.'
        question = Question.objects.filter(test=task_id, variant=variant, is_active=True).order_by('id').first()
        context['question'] = question
        answers = Answer.objects.filter(question=question, is_active=True).order_by('id')
        context['answers'] = answers
    return render(request, 'main/testing.html', context)