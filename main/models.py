from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import Signal
from django.db.models import CheckConstraint, Q

from django.utils.translation import gettext_lazy as _

from .utilities import send_activation_notification


class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name=_('Подтверждение аккаунта'),
            help_text=_('Пользовательский аккаунт, который прошел процесс подтверждения'))

    class Meta(AbstractUser.Meta):
        pass

    def __str__(self):
        str = ''
        if (len(self.last_name) > 0) or (len(self.first_name) > 0):
            str = self.last_name
            if len(self.first_name) > 0:
                if len(str) > 0:
                    str = '%s %s' % (str, self.first_name)
                else:
                    str = self.first_name
            return str
        else:
            return self.username


class Group(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name=_('Название'),
            help_text=_('Название класса или группы'))
    is_active = models.BooleanField(default=True, db_index=True, verbose_name=_('Статус отображения'),
            help_text=_('Отображение группы (класса) на сайте'))


    class Meta:
        unique_together = ('name', 'is_active')
        ordering = ('-is_active', 'name')
        verbose_name = _('Группа (класс)')
        verbose_name_plural = _('Группы (классы)')

    def __str__(self):
        if self.is_active:
            return self.name + ' [' + str(_('отображается')) + ']'
        else:
            return self.name + ' [' + str(_('не отображается')) + ']'


class Lesson(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name=_('Название'),
            help_text=_('Предмет, знания которого проверяются в тесте'))
    is_active = models.BooleanField(default=True, db_index=True, verbose_name=_('Статус отображения'),
            help_text=_('Отображение предмета на сайте'))

    class Meta:
        unique_together = ('name', 'is_active')
        ordering = ('-is_active', 'name')
        verbose_name = _('Предмет (урок)')
        verbose_name_plural = _('Предметы (уроки)')

    def __str__(self):
        if self.is_active:
            return self.name + ' [' + str(_('отображается')) + ']'
        else:
            return self.name + ' [' + str(_('не отображается')) + ']'


class Task(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, verbose_name=_('Предмет (урок)'), related_name='tasks')
    groups = models.ManyToManyField(Group, blank=True, verbose_name=_('Группы (классы)'),
            help_text=_('Названия групп (классов) где проводится тест'))
    name = models.CharField(max_length=100, db_index=True, verbose_name=_('Название теста'), help_text=_('Короткое название теста'))
    max_score = models.PositiveIntegerField(default=12, verbose_name=_('Максимальная оценка'),
                help_text=_('Максимальная оценка за все правильные ответы в тесте'))
    content = models.TextField(verbose_name=_('Описание теста'), db_index=True, help_text=_('Полное описание теста'))
    is_active = models.BooleanField(default=False, db_index=True, verbose_name=_('Статус отображения'),
                help_text=_('Отображение теста на сайте'))

    class Meta:
        # unique_together = ('name', 'lesson', 'content', 'is_active')
        ordering = ('-is_active', 'lesson', 'name')
        verbose_name = _('Тест (билет)')
        verbose_name_plural = _('Тесты (билеты)')
        constraints = [
            CheckConstraint(
                check=Q(max_score__gt=0), name='max_score_above_zero',
            ),
        ]

    def __str__(self):
        if self.is_active:
            return '%s, %s ' % (self.lesson, self.name) + '[' + str( _('отображается')) + ']'
        else:
            return '%s, %s ' % (self.lesson, self.name) + '[' + str(_('не отображается')) + ']'


class Question(models.Model):
    test = models.ForeignKey(Task, on_delete=models.PROTECT, verbose_name='Тест', related_name='questions')
    content = models.TextField(verbose_name=_('Задание'), help_text=_('Описание задаваемого вопроса в тесте'))
    score = models.FloatField(default=1.00, verbose_name=_('Балов за ответ'),
            help_text=_('Количество балов начисленных за правильный ответ'))
    variant = models.PositiveIntegerField(default=1, db_index=True, verbose_name=_('Вариант'),
            help_text=_('При создании нескольких вариантов теста'))
    type_answer = models.BooleanField(default=False, db_index=True, verbose_name=_('Множественный выбор'),
            help_text=_('Предоставить пользователю возможность выбора нескольких вариантов ответа'))
    is_active = models.BooleanField(default=True, db_index=True, verbose_name=_('Задание учтено'),
                help_text=_('Учитывать вопрос в тесте'))

    class Meta:
        #unique_together = ('content', 'test', 'variant', 'is_active')
        ordering = ('variant', 'test', 'content')
        verbose_name = _('Задание')
        verbose_name_plural = _('Задания')
        constraints = [
            CheckConstraint(
                check=Q(score__gt=0), name='score_above_zero',
            ),
            CheckConstraint(
                check=Q(variant__gte=1), name='variant_above_zero',
            ),
        ]

    def __str__(self):
        if len(self.content)>150:
            return '%s...' % (self.content[:146])
        else:
            return '%s' % (self.content)

    def save(self, *args, **kwargs):
        self.test.is_active = False
        self.test.save()
        super().save(*args, **kwargs)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.PROTECT, verbose_name=_('Вопрос'), related_name='answers')
    content = models.TextField(verbose_name=_('Ответ'), db_index=True, help_text=_('Описание возможного ответа'))
    is_true = models.BooleanField(default=False, db_index=True, verbose_name=_('Правильный ответ'),
        help_text=_('Статус правильного ответ на вопорос'))
    is_active = models.BooleanField(default=True, db_index=True, verbose_name=_('Ответ учтен'),
                help_text=_('Учитывать ответ при отображении вопроса'))

    class Meta:
        unique_together = ('content', 'question', 'is_active')
        verbose_name = _('Ответ')
        verbose_name_plural = _('Ответы')

    def __str__(self):
        if len(self.content)>150:
            return '%s...' % (self.content[:146])
        else:
            return '%s' % (self.content)

    def save(self, *args, **kwargs):
        self.question.test.is_active = False
        self.question.test.save()
        super().save(*args, **kwargs)


class Test(models.Model):
    task = models.ForeignKey(Task, on_delete=models.PROTECT, verbose_name=_('Тест'), related_name='tests')
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name=_('Пользователь'), related_name='tests')
    test_score = models.PositiveIntegerField(default=0, db_index=True, verbose_name=_('Оценка за тест'))
    is_end = models.BooleanField(default=False, db_index=True, verbose_name=_('Закончен'),
                help_text=_('Прохождение теста закончено'))
    variant = models.PositiveIntegerField(default=1, db_index=True, verbose_name=_('Вариант вопросов'),
            help_text=_('Вариант прохождения теста'))
    date_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата начала ответа'),
            help_text=_('Дата начала ответа на тест'))

    class Meta:
        unique_together = ('user', 'task')
        verbose_name = _('Сданный тест')
        verbose_name_plural = _('Сданные тесты')
        ordering = ('-id', )
        constraints = [
            CheckConstraint(
                check=Q(test_score__gte=0) | Q(test_score=None), name='test_score_non_negative',
            ),
        ]

    def __str__(self):
        return '%s - %s - %s: %d' % (self.task, self.user, str(_('Балов')),self.test_score)


class Exam(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, verbose_name=_('Тест'), related_name='exams')
    answer = models.ForeignKey(Answer, on_delete=models.PROTECT, verbose_name=_('Выбранный ответ'), related_name='exams')
    date_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата ответа'))

    class Meta:
        unique_together = ('test', 'answer')
        verbose_name = _('Ответил')
        verbose_name_plural = _('Ответили')
        ordering = ('id', )

    def __str__(self):
        if self.answer.is_true:
            str_ = '%s - (%s: %0.2f)' % (self.answer.question, _('Балов'), self.answer.question.score)
        else:
            str_ = '%s - (%s: %0.2f)' % (self.answer.question, _('Балов'), 0)
        if not self.answer.question.type_answer:
            str_ += ' - %s:' % (str(_('Один из')))
        else:
            str_ += ' - %s:' % (str(_('Все из')))
        answers = Answer.objects.filter(question=self.answer.question, is_true=True, is_active=True)
        max_len = len (answers)
        count = 0
        for answer in answers:
            count += 1
            if count < max_len:
                str_ += ' [' + answer.content +'],'
            else:
                str_ += ' [' + answer.content +'].'
        return str_


user_registrated = Signal(providing_args=['instance'])

def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])

user_registrated.connect(user_registrated_dispatcher)


