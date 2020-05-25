from django.contrib import admin
import datetime

from .models import AdvUser


class NonactivatedFilter(admin.SimpleListFilter):
    title = 'Пользователи подтверждены?'
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
            return queryset.filter(is_active=True)
        elif val == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, date_joined__date__lt=d)
        elif val == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_active=False, date_joined__date__lt=d)


class AdvUserAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'id', 'last_name', 'first_name', 'email','is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = (NonactivatedFilter,)
    fields = (
        ('username', 'email'), ('first_name', 'last_name'),
        ('is_active', 'is_staff', 'is_superuser'),
        'groups', 'user_permissions',
        ('last_login', 'date_joined'),
    )
    readonly_fields = ('last_login', 'date_joined')


admin.site.register(AdvUser, AdvUserAdmin)
