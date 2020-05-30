from django.contrib import admin
import datetime
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from crum import get_current_user
from django.contrib.admin.filters import RelatedOnlyFieldListFilter

from .models import AdvUser, Lesson, Task, Question


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


class AdditionalTaskInline(admin.StackedInline):
    model = Task
    fields = ('author', ('name', 'max_score'), 'content', ('is_active', 'public_at'),)
    readonly_fields = ('public_at', 'author', )
    extra = 0


class LessonAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = (AdditionalTaskInline,)


admin.site.register(Lesson, LessonAdmin)


class AdditionalQuestionInline(admin.StackedInline):
    model = Question
    extra = 0


class TaskAdmin(admin.ModelAdmin):
    list_display = ( '__str__', 'lesson', 'author','max_score', 'is_active', 'public_at',)
    list_filter = ('is_active', 'lesson', ('lesson', RelatedOnlyFieldListFilter), ('author', RelatedOnlyFieldListFilter),)
    search_fields = ('name', 'lesson',)
    fields = (
        ('lesson', 'author', 'name'),
        'content',
        ('max_score', 'is_active', 'public_at')
    )
    readonly_fields = ('public_at', 'author')
    inlines = (AdditionalQuestionInline,)
    list_editable = ('is_active', )





admin.site.register(Task, TaskAdmin)
