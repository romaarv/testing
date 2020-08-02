from django.contrib import admin
import datetime
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.db import models, IntegrityError
from django.forms import Textarea, NumberInput, TextInput
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from modeltranslation.admin import TranslationAdmin


from .models import AdvUser, Lesson, Task, Question, Answer, Group, Test, Exam
from .utilities import send_activation_notification

def send_activation_notifications(modeladmin, request,queryset):
    for rec in queryset:
        if not rec.is_activated:
            send_activation_notification(rec)
    modeladmin.message_user(request, 'Письма с оповещением отправлены')
send_activation_notifications.short_description = 'Отправка писем с оповещениями об активации'


class NonactivatedFilter(admin.SimpleListFilter):
    title = 'Подтверждение аккаунта'
    parameter_name = 'actstate'

    def lookups(self, request, model_admin):
        return (
            ('activated', 'Прошли'),
            ('threedays', 'Не прошли более 3х дней'),
            ('week', 'Не прошли более недели'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'activated':
            return queryset.filter(is_active=True, is_activated=True)
        elif val == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, is_activated=False, date_joined__date__lt=d)
        elif val == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_active=False, is_activated=False, date_joined__date__lt=d)


@admin.register(AdvUser)
class AdvUserAdmin(UserAdmin, admin.ModelAdmin):
    list_display = ('__str__', 'username', 'email', 'is_active', 'is_activated', 'is_staff', 'is_superuser', 'id')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = (NonactivatedFilter, 'is_active', 'is_staff', 'is_superuser', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_activated', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_editable = ('is_active', 'is_activated', 'is_staff', 'is_superuser')
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activation_notifications, )


class LessonAdmin(TranslationAdmin):
    list_display = ('name', 'is_active', 'creator', 'modified')
    search_fields = ('name', )
    list_editable = ('is_active', )
    list_filter = ('is_active', )

    def creator(self, rec):
        str = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(Lesson),
                object_id=rec.id).order_by('action_time')[:1]
        if len(str) > 0:
            return '%s - %s' % (str[0].user, str[0].action_time.strftime('%d.%m.%Y %H:%M:%S'))
        else:
            return None
    creator.short_description = 'Создание'

    def modified(self, rec):
        str = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(Lesson),
                object_id=rec.id).order_by('-action_time')[:1]
        if len(str) > 0:
            return '%s - %s' % (str[0].user, str[0].action_time.strftime('%d.%m.%Y %H:%M:%S'))
        else:
            return None
    modified.short_description = 'Последнее изменение'

admin.site.register(Lesson, LessonAdmin)

class GroupAdmin(TranslationAdmin):
    list_display = ('name', 'is_active', 'creator', 'modified')
    search_fields = ('name',)
    list_editable = ('is_active', )
    list_filter = ('is_active', )

    def creator(self, rec):
        str = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(Group),
                object_id=rec.id).order_by('action_time')[:1]
        if len(str) > 0:
            return '%s - %s' % (str[0].user, str[0].action_time.strftime('%d.%m.%Y %H:%M:%S'))
        else:
            return None
    creator.short_description = 'Создание'

    def modified(self, rec):
        str = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(Group),
                object_id=rec.id).order_by('-action_time')[:1]
        if len(str) > 0:
            return '%s - %s' % (str[0].user, str[0].action_time.strftime('%d.%m.%Y %H:%M:%S'))
        else:
            return None
    modified.short_description = 'Последнее изменение'

admin.site.register(Group, GroupAdmin)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'lesson', 'task_groups','max_score', 'is_active', 'creator', 'modified')
    list_filter = ('is_active', 'lesson', 'groups')
    search_fields = ('name', 'lesson__name')
    fields = (('name', 'lesson', 'is_active'), ('content', 'max_score'), 'groups')
    filter_horizontal = ('groups', )
    list_editable = ('is_active', )
    is_show = False
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(
                attrs={'rows': 1, 'cols': 90, 'style': 'height: 4em;'}),
        },
        models.PositiveIntegerField: {
            'widget': TextInput(
            attrs={'min': '1', 'type': 'number'}),
        },
    }

    def creator(self, rec):
        str = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(Task),
                object_id=rec.id).order_by('action_time')[:1]
        if len(str) > 0:
            return '%s - %s' % (str[0].user, str[0].action_time.strftime('%d.%m.%Y %H:%M:%S'))
        else:
            return None
    creator.short_description = 'Создание'

    def modified(self, rec):
        str = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(Task),
            object_id=rec.id).order_by('-action_time')[:1]
        if len(str) > 0:
            return '%s - %s' % (str[0].user, str[0].action_time.strftime('%d.%m.%Y %H:%M:%S'))
        else:
            return None
    modified.short_description = 'Последнее изменение'

    def save_model(self, request, obj, form, change):
        self.is_show = obj.is_active
        super().save_model(request, obj, form, change)

    def response_change(self, request, obj):
        if (obj.is_active == False) and (self.is_show != obj.is_active):
            messages.warning(request, 
                    mark_safe('Внесенные измененения требует повторной проверки. Тест (билет) "\
                        <a href="/admin/main/task/%d/change/">%s</a>" отмечен как неотображаемый.' % (obj.id ,obj)))
        self.is_show = obj.is_active
        return super().response_change(request, obj)

    def task_groups(self, rec):
        count_type = 100    #Количество символов для отображения на экране
        str = ''
        max_len = len(rec.groups.filter(is_active=True))
        if max_len > 0:
            str = 'Группы (отображ): '
            count = 0
            for group in rec.groups.filter(is_active=True):
                count += 1
                str += '%s' % (group.name)
                if count < max_len:
                    str += ', '
            if len(str) > count_type:
                str = '%s...' % (str[:count_type - 5])
            else:
                str = '%s.' % (str)
        if len(str) < count_type - 25:
            max_len = len(rec.groups.filter(is_active=False))
            if max_len > 0:
                count = 0
                if len(str) > 0:
                    str += ' Группы (не отображ): '
                else:
                    str = 'Группы (не отображ): '
                for group in rec.groups.filter(is_active=False):
                    count +=1
                    str += '%s' % (group.name)
                    if count < max_len:
                        str += ', '
                if len(str) > count_type:
                    str = '%s...' % (str[:count_type - 5])
                else:
                    str = '%s.' % (str)
        if len(str) == 0:
            str = 'Группы не определены'
        return '%s' % (str)
    task_groups.short_description = 'Номера групп (классов)'

admin.site.register(Task, TaskAdmin)


class AdditionalAnswerInline(admin.TabularInline):
    model = Answer
    fields = (
        'content',
        ('is_true', 'is_active')
    )
    extra = 0
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(
            attrs={'rows': 1,
                'cols': 90,
                'style': 'height: 1em;'})
        },
    }


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'test', 'variant', 'is_active', 'creator', 'modified')
    list_editable = ('is_active', )
    search_fields = ('content', 'test__name', 'test__lesson__name', 'test__groups__name', 'variant')
    list_filter = ('is_active','test__lesson', 'test__groups', 'variant', 'test')
    fields = (
        'test',
        'content',
        ('score', 'type_answer'),
        ('is_active', 'variant')
    )
    inlines = (AdditionalAnswerInline,)
    raw_id_fields = ('test', )
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(
            attrs={'rows': 1,
                'cols': 90,
                'style': 'height: 5em;'})
        },
    }

    def creator(self, rec):
        str = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(Question),
                object_id=rec.id).order_by('action_time')[:1]
        if len(str) > 0:
            return '%s - %s' % (str[0].user, str[0].action_time.strftime('%d.%m.%Y %H:%M:%S'))
        else:
            return None
    creator.short_description = 'Создание'

    def modified(self, rec):
        str = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(Question),
                object_id=rec.id).order_by('-action_time')[:1]
        if len(str) > 0:
            return '%s - %s' % (str[0].user, str[0].action_time.strftime('%d.%m.%Y %H:%M:%S'))
        else:
            return None
    modified.short_description = 'Последнее изменение'

    def save_model(self, request, obj, form, change):
        if obj.test.is_active:
            messages.warning(request, 
                    mark_safe('Внесенные измененения требует повторной проверки. Тест (билет) "\
                        <a href="/admin/main/task/%d/change/">%s</a>" отмечен как неотображаемый.' % (obj.test.id ,obj.test)))
        obj.save()

admin.site.register(Question, QuestionAdmin)


class AdditionalExamInline(admin.TabularInline):
    model = Exam
    fields = ('answer', 'date_at')
    readonly_fields = ('answer', 'date_at')
    extra = 0
    can_delete = False


class TestAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'score','test_groups','start_at', 'end_at')
    readonly_fields = ('task', 'user', 'test_score', 'is_end')
    search_fields = ('task__name', 'task__lesson__name', 'task__groups__name', 'test_score', 
        'user__last_name', 'user__first_name', 'user__username')
    list_filter = ('is_end', 'task__lesson', 'task__groups', 'test_score', 'task')
    inlines = (AdditionalExamInline, )


    def start_at(self, rec):
        date_ = Exam.objects.filter(test=rec.id).order_by('id').first()
        return '%s' % (date_.date_at.strftime('%d.%m.%Y %H:%M:%S'))
    start_at.short_description = 'Начат'

    def end_at(self, rec):
        if rec.is_end:
            date_ = Exam.objects.filter(test=rec.id).order_by('id').last()
            return '%s' % (date_.date_at.strftime('%d.%m.%Y %H:%M:%S'))
        else:
            return 'Нет'
    end_at.short_description = 'Закончен'

    def score(self, rec):
        task = Task.objects.filter(id=rec.task.id)
        return '%d из %d' % (rec.test_score, task[0].max_score)
    score.short_description = 'Оценка'

    def test_groups(self, rec):
        count_type = 100    #Количество символов для отображения на экране
        str_ = ''
        max_len = len(rec.task.groups.filter(is_active=True))
        if max_len > 0:
            str_ = 'Группы (отображ): '
            count = 0
            for group in rec.task.groups.filter(is_active=True):
                count += 1
                str_ += '%s' % (group.name)
                if count < max_len:
                    str_ += ', '
            if len(str_) > count_type:
                str_ = '%s...' % (str_[:count_type - 5])
            else:
                str_ = '%s.' % (str_)
        if len(str_) < count_type - 25:
            max_len = len(rec.task.groups.filter(is_active=False))
            if max_len > 0:
                count = 0
                if len(str_) > 0:
                    str_ += ' Группы (не отображ): '
                else:
                    str_ = 'Группы (не отображ): '
                for group in rec.task.groups.filter(is_active=False):
                    count +=1
                    str_ += '%s' % (group.name)
                    if count < max_len:
                        str_ += ', '
                if len(str_) > count_type:
                    str_ = '%s...' % (str_[:count_type - 5])
                else:
                    str_ = '%s.' % (str_)
        if len(str_) == 0:
            str_ = 'Группы не определены'
        return '%s' % (str_)
    test_groups.short_description = 'Номера групп (классов)'

admin.site.register(Test, TestAdmin)


admin.site.register(LogEntry)