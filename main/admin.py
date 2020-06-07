from django.contrib import admin
import datetime
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.forms import Textarea, SelectMultiple
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType

from .models import AdvUser, Lesson, Task, Question, Answer, Group
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


class LessonAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name', )
    list_editable = ('is_active', )
    list_filter = ('is_active', )

admin.site.register(Lesson, LessonAdmin)


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'creator')
    search_fields = ('name',)
    list_editable = ('is_active', )
    list_filter = ('is_active', )

    def creator(self, rec):
        str = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(Group), object_id=rec.id)
        return '%s - %s -%s' % (str[0].user, str[0].action_time.strftime('%d.%m.%Y %H:%M:%S'), datetime.datetime.today().strftime('%d.%m.%Y %H:%M:%S'))

        def get_queryset(self):
            return self.first()

    creator.short_description = 'Создатель'

admin.site.register(Group, GroupAdmin)


class AdditionalQuestionInline(admin.TabularInline):
    model = Question
    fields = (
        'content',
        ('score', 'type_answer'),
        ('is_active', 'variant')
    )
    extra = 0
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(
            attrs={'rows': 1,
                'cols': 90,
                'style': 'height: 4em;'})
        },
    }


class TaskAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'lesson', 'task_groups','max_score', 'is_active')
    list_filter = ('is_active', 'lesson', 'groups')
    search_fields = ('name', 'lesson__name')
    fields = (('name', 'lesson'), ('content', 'max_score', 'is_active'), 'groups')
    filter_horizontal = ('groups', )
    inlines = (AdditionalQuestionInline, )
    list_editable = ('is_active', )
    is_show = False
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(
            attrs={'rows': 1,
                'cols': 90,
                'style': 'height: 4em;'}),
        },
         # models.ManyToManyField: {'widget': SelectMultiple(attrs={'size':'5', 'style': 'color:blue;width:250px'})},
    }


    def save_model(self, request, obj, form, change):
        self.is_show = obj.is_active
        super().save_model(request, obj, form, change)

    def response_change(self, request, obj):
        if (obj.is_active == False) and (self.is_show != obj.is_active):
            messages.warning(request, 
                    mark_safe('Внесенные измененения требует повторной проверки теста (билета). Тест (билет) "\
                        <a href="/admin/main/task/%d/change/">%s</a>" отмечен как неопубликованный.' % (obj.id ,obj)))
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
    list_display = ('__str__', 'test', 'variant', 'is_active')
    list_editable = ('is_active', )
    search_fields = ('content', 'test__name')
    list_filter = ('is_active', 'test__lesson', 'variant', 'test')
    fields = (
        'test',
        'content',
        ('score', 'type_answer'),
        ('is_active', 'variant')
    )
    inlines = (AdditionalAnswerInline,)
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(
            attrs={'rows': 1,
                'cols': 90,
                'style': 'height: 5em;'})
        },
    }

    def save_model(self, request, obj, form, change):
        if obj.test.is_active:
            messages.warning(request, 
                    mark_safe('Внесенные измененения требует повторной проверки теста (билета). Тест (билет) "\
                        <a href="/admin/main/task/%d/change/">%s</a>" отмечен как неопубликованный.' % (obj.id ,obj)))
        obj.save()


admin.site.register(Question, QuestionAdmin)

admin.site.register(LogEntry)