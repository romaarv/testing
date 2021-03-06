from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import AdvUser, user_registrated


class ChangeUserInfoForm(forms.ModelForm):
    username = forms.CharField(required=True, label=_('Логин'))
    email = forms.EmailField(required=True, label=_('Адрес электронной почты'))
    first_name = forms.CharField(required=True, label=_('Имя'))
    last_name = forms.CharField(required=True, label=_('Фамилия'))

    class Meta:
        model = AdvUser
        fields = ('username', 'first_name', 'last_name', 'email')


class RegisterUserForm(forms.ModelForm):
    username = forms.CharField(required=True, label=_('Логин'))
    email = forms.EmailField(required=True, label=_('Адрес электронной почты'))
    first_name = forms.CharField(required=True, label=_('Имя'))
    last_name = forms.CharField(required=True, label=_('Фамилия'))
    password1 = forms.CharField(label=_('Пароль'), widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label=_('Пароль (повторно)'), widget=forms.PasswordInput,
        help_text=_('Введите тот же самый пароль еще раз для проверки'))

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        try:
            password_validation.validate_password(password1, self.instance)
        except forms.ValidationError as error:
            self.add_error('password1', error)
        return password1

    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError(_('Введенные пароли не совпадают'),
                code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registrated.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = AdvUser
        fields = ('first_name', 'last_name', 'email', 'username',
            'password1', 'password2')