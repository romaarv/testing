from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractUser


class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=False, db_index=True, verbose_name='Статус подтверждения',
                    help_text='Пользователь, прошедший процесс подтверждения')

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
    name = models.CharField(max_length=25, db_index=True, verbose_name='Название',
            help_text='Предмет, знания которого проверяются в тесте')

    def __str__(self):
        return '%s' % (self.name)


class Task(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, verbose_name='Предмет', related_name='tests')
    name = models.CharField(max_length=100, verbose_name='Название ', help_text='Короткое название теста')
    max_score = models.PositiveIntegerField(default=12, verbose_name='Максимальная оценка',
                help_text='Максимальное количество балов которые можно набрать за все правильные ответы в тесте')
    content = models.TextField(verbose_name='Описание', help_text='Детальное описание теста')
    is_active = models.BooleanField(default=False, db_index=True, verbose_name='Статус публикации',
                help_text='Вопросы составлены и тест готов к публикации')
    public_at = models.DateTimeField(default=None, blank=True, db_index=True, verbose_name='Дата публикации',
                help_text='Дата публикации теста')

    def __str__(self):
        if is_active:
            return '%s от %s' % (self.name, self.public_at.strftime('%d.%m.%Y'))
        else:
            return '%s' % (self.name)


class Question(models.Model):
    test = models.ForeignKey(Task, on_delete=models.PROTECT, verbose_name='Тест', related_name='questions')
    content = models.TextField(verbose_name='Вопрос', help_text='Описание задаваемого вопроса в тесте')
    score = models.FloatField(default=1.00, verbose_name='Оценка за ответ',
            help_text='Количество балов начисленных за правильный ответ')
    variant = models.PositiveIntegerField(default=1, db_index=True, verbose_name='№ варианта',
            help_text='При создании нескольких вариантов теста')
    type_answer = models.BooleanField(default=False, verbose_name='Множественный выбор',
            help_text='Дать возможность выбора нескольких вариантов ответа')

    def __str__(self):
        if len(self.content)>100:
            return '%s - %s...' % (self.test, self.content[:96])
        else:
            return '%s - %s' % (self.test, self.content)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.PROTECT, verbose_name='Вопрос', related_name='answers')
    content = models.TextField(verbose_name='Ответ', help_text='Описание возможного ответа')
    is_true = models.BooleanField(default=False, db_index=True, verbose_name='Правильный ответ', help_text='Статус правильного ответ на вопорос')

    def __str__(self):
        if len(self.content)>100:
            return '%s...' % (self.content[:96])
        else:
            return '%s' % (self.content)


class Exam(models.Model):
    user = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='exams')
    answer = models.ForeignKey(Answer, on_delete=models.PROTECT, verbose_name='Выбранный ответ', related_name='exams')
    tasks = models.ManyToManyField(Task, through='Test')

    def __str__(self):
        return '%s' % (self.user)


class Test(models.Model):
    task = models.ForeignKey(Task, on_delete=models.PROTECT)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    test_start = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Тест начат')
    test_end = models.DateTimeField(default=None, blank=True, db_index=True, verbose_name='Тест закончен')
    test_score = models.PositiveIntegerField(default=None, blank=True, db_index=True, verbose_name='Оценка')


