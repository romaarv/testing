# Generated by Django 3.0.6 on 2020-06-03 20:29

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdvUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_activated', models.BooleanField(db_index=True, default=True, help_text='Пользовательский аккаунт, который прошел процесс подтверждения', verbose_name='Подтверждение аккаунта')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(db_index=True, help_text='Описание возможного ответа', verbose_name='Ответ')),
                ('is_true', models.BooleanField(db_index=True, default=False, help_text='Статус правильного ответ на вопорос', verbose_name='Правильный ответ')),
                ('is_active', models.BooleanField(db_index=True, default=True, help_text='Учитывать ответ при отображение вопроса', verbose_name='Ответ учтен')),
            ],
            options={
                'verbose_name': 'Ответ',
                'verbose_name_plural': 'Ответы',
            },
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='exams', to='main.Answer', verbose_name='Выбранный ответ')),
            ],
            options={
                'verbose_name': 'Ответил',
                'verbose_name_plural': 'Ответили',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='№ класса или группы', max_length=100, verbose_name='Название')),
                ('is_active', models.BooleanField(db_index=True, default=True, help_text='Опубликовать группу на сайте', verbose_name='Отображение на сайте')),
            ],
            options={
                'verbose_name': 'Группа',
                'verbose_name_plural': 'Группы',
                'ordering': ('name',),
                'unique_together': {('name',)},
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Предмет, знания которого проверяются в тесте', max_length=100, verbose_name='Название')),
                ('is_active', models.BooleanField(db_index=True, default=True, help_text='Опубликовать предмет на сайте', verbose_name='Отображение на сайте')),
            ],
            options={
                'verbose_name': 'Предмет',
                'verbose_name_plural': 'Предметы',
                'ordering': ('name',),
                'unique_together': {('name',)},
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, help_text='Короткое название теста', max_length=100, verbose_name='Название теста')),
                ('max_score', models.PositiveIntegerField(default=12, help_text='Максимальное количество балов которые можно набрать за все правильные ответы в тесте', verbose_name='Максимальная оценка')),
                ('content', models.TextField(db_index=True, help_text='Детальное описание теста', verbose_name='Описание теста')),
                ('is_active', models.BooleanField(db_index=True, default=False, help_text='Опубликовать тест на сайте', verbose_name='Отображение на сайте')),
                ('groups', models.ManyToManyField(to='main.Group')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tasks', to='main.Lesson', verbose_name='Предмет')),
            ],
            options={
                'verbose_name': 'Тест',
                'verbose_name_plural': 'Тесты',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_score', models.FloatField(blank=True, db_index=True, default=None, verbose_name='Оценка')),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Exam')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.Task')),
            ],
            options={
                'verbose_name': 'Сданный тест',
                'verbose_name_plural': 'Сданные тесты',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(help_text='Описание задаваемого вопроса в тесте', verbose_name='Задание')),
                ('score', models.FloatField(default=1.0, help_text='Количество балов начисленных за правильный ответ', verbose_name='Балов за ответ')),
                ('variant', models.PositiveIntegerField(db_index=True, default=1, help_text='При создании нескольких вариантов теста', verbose_name='№ варианта')),
                ('type_answer', models.BooleanField(db_index=True, default=False, help_text='Возможность выбора нескольких вариантов ответа', verbose_name='Множественный выбор')),
                ('is_active', models.BooleanField(db_index=True, default=True, help_text='Учитывать вопрос в тесте', verbose_name='Задание учтено')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='questions', to='main.Task', verbose_name='Тест')),
            ],
            options={
                'verbose_name': 'Задание',
                'verbose_name_plural': 'Задания',
                'ordering': ('variant', 'test', 'content'),
            },
        ),
        migrations.AddField(
            model_name='exam',
            name='tasks',
            field=models.ManyToManyField(through='main.Test', to='main.Task'),
        ),
        migrations.AddField(
            model_name='exam',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exams', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='answers', to='main.Question', verbose_name='Вопрос'),
        ),
        migrations.AddConstraint(
            model_name='test',
            constraint=models.CheckConstraint(check=models.Q(('test_score__gte', 0), ('test_score', None), _connector='OR'), name='test_score_non_negative'),
        ),
        migrations.AddConstraint(
            model_name='task',
            constraint=models.CheckConstraint(check=models.Q(max_score__gt=0), name='max_score_above_zero'),
        ),
        migrations.AlterUniqueTogether(
            name='task',
            unique_together={('name', 'lesson', 'content')},
        ),
        migrations.AddConstraint(
            model_name='question',
            constraint=models.CheckConstraint(check=models.Q(score__gt=0), name='score_above_zero'),
        ),
        migrations.AddConstraint(
            model_name='question',
            constraint=models.CheckConstraint(check=models.Q(variant__gte=1), name='variant_above_zero'),
        ),
        migrations.AlterUniqueTogether(
            name='question',
            unique_together={('content', 'test', 'variant')},
        ),
        migrations.AlterUniqueTogether(
            name='exam',
            unique_together={('user', 'answer')},
        ),
        migrations.AlterUniqueTogether(
            name='answer',
            unique_together={('content', 'question')},
        ),
    ]
