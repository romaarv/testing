from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.dispatch import Signal
from crum import get_current_user

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


class Lesson(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Название',
            help_text='Предмет, знания которого проверяются в тесте')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Отображение на сайте',
            help_text='Опубликовать предмет на сайте')
    last_modified = models.ForeignKey(AdvUser, on_delete=models.PROTECT, verbose_name='Последнее изменение',
            related_name='lessons_modified')
    modified_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата изменения',
                help_text='Дата последнего изменения')

    class Meta:
        unique_together = ('name',)
        ordering = ('name',)
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'

    def __str__(self):
        return '%s' % (self.name)

    def save(self, *args, **kwargs):
        self.last_modified = get_current_user()
        super().save(*args, **kwargs)


class Task(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, verbose_name='Предмет', related_name='tasks')
    author = models.ForeignKey(AdvUser, on_delete=models.PROTECT, verbose_name='Автор теста', related_name='tasks')
    name = models.CharField(max_length=100, db_index=True, verbose_name='Название теста', help_text='Короткое название теста')
    max_score = models.PositiveIntegerField(default=12, verbose_name='Максимальная оценка',
                help_text='Максимальное количество балов которые можно набрать за все правильные ответы в тесте')
    content = models.TextField(verbose_name='Описание теста', db_index=True, help_text='Детальное описание теста')
    is_active = models.BooleanField(default=False, db_index=True, verbose_name='Отображение на сайте',
                help_text='Опубликовать тест на сайте')
    public_at = models.DateTimeField(default=None, blank=True, null=True, db_index=True, verbose_name='Дата публикации',
                help_text='Дата публикации теста на сайте')
    last_modified = models.ForeignKey(AdvUser, on_delete=models.PROTECT, verbose_name='Последнее изменение',
            related_name='tasks_modified')
    modified_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата изменения',
                help_text='Дата последнего изменения')

    class Meta:
        unique_together = ('lesson', 'author', 'name')
        ordering = ('-public_at',)
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'

    def __str__(self):
        if len(self.name)>100:
            name = '%s...' % (self.name[:96])
        else:
            name =  '%s' % (self.name)
        if self.is_active:
            return '%s [%s - %s, %s]' % (name, self.lesson, self.author.last_name, self.public_at.strftime('%d.%m.%Y'))
        else:
            return '%s [%s - %s, не опубликован]' % (name, self.author.last_name, self.lesson)

    def save(self, *args, **kwargs):
        if self.is_active == True:
            self.public_at = datetime.now()
        else:
            self.public_at = None
        if self.author_id == None:
            self.author = get_current_user()
            # if self.author = get_current_user()
        self.last_modified = get_current_user()
        super().save(*args, **kwargs)


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
    last_modified = models.ForeignKey(AdvUser, on_delete=models.PROTECT, verbose_name='Последнее изменение',
            related_name='questions_modified')
    modified_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата изменения',
                help_text='Дата последнего изменения')

    class Meta:
        unique_together = ('test', 'content', 'variant')
        ordering = ('variant', 'test', 'content')
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'

    def __str__(self):
        if len(self.content)>100:
            return '%s...' % (self.content[:96])
        else:
            return '%s' % (self.content)

    def save(self, *args, **kwargs):
        self.last_modified = get_current_user()
        super().save(*args, **kwargs)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.PROTECT, verbose_name='Вопрос', related_name='answers')
    content = models.TextField(verbose_name='Ответ', db_index=True, help_text='Описание возможного ответа')
    is_true = models.BooleanField(default=False, db_index=True, verbose_name='Правильный ответ',
        help_text='Статус правильного ответ на вопорос')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Ответ учтен',
                help_text='Учитывать ответ при отображение вопроса')
    last_modified = models.ForeignKey(AdvUser, on_delete=models.PROTECT, verbose_name='Последнее изменение',
            related_name='answers_modified')
    modified_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата изменения',
                help_text='Дата последнего изменения')

    class Meta:
        unique_together = ('question', 'content')
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'

    def __str__(self):
        if len(self.content)>30:
            return '%s...' % (self.content[:26])
        else:
            return '%s' % (self.content)

    def save(self, *args, **kwargs):
        self.last_modified = get_current_user()
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
    test_start = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Тест начат')
    test_end = models.DateTimeField(default=None, blank=True, db_index=True, verbose_name='Тест закончен')
    test_score = models.PositiveIntegerField(default=None, blank=True, db_index=True, verbose_name='Оценка')

    class Meta:
        verbose_name = 'Сданный тест'
        verbose_name_plural = 'Сданные тесты'

    def __str__(self):
        if test_end is None:
            return '%s - %s - Тест не закончен' % (self.exam.user, self.task)
        else:
            return '%s - %s - Балов: %d' % (self.exam.user, self.task, self.test_score)


user_registrated = Signal(providing_args=['instance'])

def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])

user_registrated.connect(user_registrated_dispatcher)


