from django.contrib import admin
import datetime
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from crum import get_current_user
from django.db import models
from django.forms import Textarea

from .models import AdvUser, Lesson, Task, Question, Answer
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


class AdditionalTaskInline(admin.TabularInline):
    model = Task
    fields = (('name', 'author', 'max_score'), 'content', ('is_active', 'public_at', 'last_modified', 'modified_at'))
    readonly_fields = ('public_at', 'author', 'last_modified', 'modified_at')
    extra = 0
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(
            attrs={'rows': 1,
                'cols': 90,
                'style': 'height: 4em;'})
        },
    }


class LessonAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'last_modified', 'modified_at')
    search_fields = ('name', )
    fields = (
        ('name', 'is_active', 'last_modified', 'modified_at'),
    )
    list_filter = ('is_active', )
    readonly_fields = ('last_modified', 'modified_at')
    inlines = (AdditionalTaskInline, )


admin.site.register(Lesson, LessonAdmin)


class AdditionalQuestionInline(admin.TabularInline):
    model = Question
    fields = (
        'content',
        ('score', 'type_answer'),
        ('is_active', 'variant', 'last_modified', 'modified_at')
    )
    readonly_fields = ('last_modified', 'modified_at', )
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
    list_display = ( 'name', 'lesson', 'author', 'public_at', 'max_score', 'is_active', 'last_modified', 'modified_at')
    list_filter = ('is_active', 'lesson')
    search_fields = ('name', 'author__last_name', 'author__last_name')
    fields = (('name', 'lesson', 'author'), ('content', 'max_score'), ('is_active', 'public_at', 'last_modified', 'modified_at'))
    readonly_fields = ('public_at', 'author', 'last_modified', 'modified_at')
    inlines = (AdditionalQuestionInline,)
    list_editable = ('is_active', )
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(
            attrs={'rows': 1,
                'cols': 90,
                'style': 'height: 4em;'})
        },
    }

admin.site.register(Task, TaskAdmin)


class AdditionalAnswerInline(admin.TabularInline):
    model = Answer
    fields = (
        'content',
        ('is_true', 'is_active', 'last_modified', 'modified_at')
    )
    readonly_fields = ('last_modified', 'modified_at', )
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
    list_display = ('__str__', 'test', 'variant', 'is_active', 'last_modified', 'modified_at')
    list_editable = ('is_active', )
    search_fields = ('content', 'test__name', 'test__author__last_name', 'test__author__first_name')
    list_filter = ('is_active', 'test__lesson', 'variant', 'test')
    fields = (
        'test',
        'content',
        ('score', 'type_answer'),
        ('is_active', 'variant', 'last_modified', 'modified_at')
    )
    readonly_fields = ('last_modified', 'modified_at')
    inlines = (AdditionalAnswerInline,)
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(
            attrs={'rows': 1,
                'cols': 90,
                'style': 'height: 5em;'})
        },
    }

admin.site.register(Question, QuestionAdmin)