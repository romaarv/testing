from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import Signal
from django.db.models import CheckConstraint, Q

from .utilities import send_activation_notification


class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Подтверждение аккаунта',
            help_text='Пользовательский аккаунт, который прошел процесс подтверждения')

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
    name = models.CharField(max_length=100, db_index=True, verbose_name='Название',
            help_text='Название класса или группы')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Отображение на сайте',
            help_text='Опубликовать группу на сайте')


    class Meta:
        unique_together = ('name', 'is_active')
        ordering = ('name',)
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        if self.is_active:
            return '%s [Отображается на сайте]' % (self.name)
        else:
            return '%s [Неотображается на сайте]' % (self.name)


class Lesson(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Название',
            help_text='Предмет, знания которого проверяются в тесте')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Отображение на сайте',
            help_text='Опубликовать предмет на сайте')


    class Meta:
        unique_together = ('name', 'is_active')
        ordering = ('name',)
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'

    def __str__(self):
        return '%s' % (self.name)


class Task(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, verbose_name='Предмет', related_name='tasks')
    groups = models.ManyToManyField(Group, verbose_name='Названия', help_text='Название класса или группы')
    name = models.CharField(max_length=100, db_index=True, verbose_name='Название теста', help_text='Короткое название теста')
    max_score = models.PositiveIntegerField(default=12, verbose_name='Максимальная оценка',
                help_text='Максимальное количество балов которые можно набрать за все правильные ответы в тесте')
    content = models.TextField(verbose_name='Описание теста', db_index=True, help_text='Детальное описание теста')
    is_active = models.BooleanField(default=False, db_index=True, verbose_name='Отображение на сайте',
                help_text='Опубликовать тест на сайте')


    class Meta:
        unique_together = ('name', 'lesson', 'content', 'is_active')
        ordering = ('id',)
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'
        constraints = [
            CheckConstraint(
                check=Q(max_score__gt=0), name='max_score_above_zero',
            ),
        ]

    def __str__(self):
        if len(self.name)>100:
            name = '%s...' % (self.name[:96])
        else:
            name = '%s' % (self.name)
        return '%s [%s - %s]' % (name, self.lesson, self.groups.name)



class Question(models.Model):
    test = models.ForeignKey(Task, on_delete=models.PROTECT, verbose_name='Тест', related_name='questions')
    content = models.TextField(verbose_name='Задание', help_text='Описание задаваемого вопроса в тесте')
    score = models.FloatField(default=1.00, verbose_name='Балов за ответ',
            help_text='Количество балов начисленных за правильный ответ')
    variant = models.PositiveIntegerField(default=1, db_index=True, verbose_name='№ варианта',
            help_text='При создании нескольких вариантов теста')
    type_answer = models.BooleanField(default=False, db_index=True, verbose_name='Множественный выбор',
            help_text='Возможность выбора нескольких вариантов ответа')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Задание учтено',
                help_text='Учитывать вопрос в тесте')


    class Meta:
        unique_together = ('content', 'test', 'variant', 'is_active')
        ordering = ('variant', 'test', 'content')
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        constraints = [
            CheckConstraint(
                check=Q(score__gt=0), name='score_above_zero',
            ),
            CheckConstraint(
                check=Q(variant__gte=1), name='variant_above_zero',
            ),
        ]

    def __str__(self):
        if len(self.content)>100:
            return '%s...' % (self.content[:96])
        else:
            return '%s' % (self.content)

    def save(self, *args, **kwargs):
        self.test.is_active = False
        self.test.save()
        super().save(*args, **kwargs)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.PROTECT, verbose_name='Вопрос', related_name='answers')
    content = models.TextField(verbose_name='Ответ', db_index=True, help_text='Описание возможного ответа')
    is_true = models.BooleanField(default=False, db_index=True, verbose_name='Правильный ответ',
        help_text='Статус правильного ответ на вопорос')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Ответ учтен',
                help_text='Учитывать ответ при отображение вопроса')


    class Meta:
        unique_together = ('content', 'question', 'is_active')
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        if len(self.content)>100:
            return '%s...' % (self.content[:96])
        else:
            return '%s' % (self.content)

    def save(self, *args, **kwargs):
        self.question.test.is_active = False
        self.question.test.save()
        super().save(*args, **kwargs)


class Exam(models.Model):
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='exams')
    answer = models.ForeignKey(Answer, on_delete=models.PROTECT, verbose_name='Выбранный ответ', related_name='exams')
    tasks = models.ManyToManyField(Task, through='Test')

    class Meta:
        unique_together = ('user', 'answer')
        verbose_name = 'Ответил'
        verbose_name_plural = 'Ответили'

    def __str__(self):
        if self.answer.is_true:
            return '%s - %s - Балов: %0.2f' % (self.user, self.answer, self.answer.question.score)
        else:
            return '%s - %s - Балов: %0.2f' % (self.user, self.answer, 0)


class Test(models.Model):
    task = models.ForeignKey(Task, on_delete=models.PROTECT)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    test_score = models.FloatField(default=None, blank=True, db_index=True, verbose_name='Оценка')

    class Meta:
        verbose_name = 'Сданный тест'
        verbose_name_plural = 'Сданные тесты'
        constraints = [
            CheckConstraint(
                check=Q(test_score__gte=0) | Q(test_score=None), name='test_score_non_negative',
            ),
        ]

    def __str__(self):
        if test_end is None:
            return '%s - %s - Тест не закончен' % (self.exam.user, self.task)
        else:
            return '%s - %s - Балов: %d' % (self.exam.user, self.task, self.test_score)


user_registrated = Signal(providing_args=['instance'])

def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])

user_registrated.connect(user_registrated_dispatcher)


