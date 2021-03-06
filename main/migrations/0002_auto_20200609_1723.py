# Generated by Django 3.0.7 on 2020-06-09 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'ordering': ('-is_active', 'name'), 'verbose_name': 'Группа (класс)', 'verbose_name_plural': 'Группы (классы)'},
        ),
        migrations.AlterModelOptions(
            name='lesson',
            options={'ordering': ('-is_active', 'name'), 'verbose_name': 'Предмет (урок)', 'verbose_name_plural': 'Предметы (уроки)'},
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ('-is_active', 'lesson', 'name'), 'verbose_name': 'Тест (билет)', 'verbose_name_plural': 'Тесты (билеты)'},
        ),
        migrations.AlterField(
            model_name='group',
            name='is_active',
            field=models.BooleanField(db_index=True, default=True, help_text='Отображение группы (класса) на сайте', verbose_name='Статус отображения'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='is_active',
            field=models.BooleanField(db_index=True, default=True, help_text='Отображение предмета на сайте', verbose_name='Статус отображения'),
        ),
        migrations.AlterField(
            model_name='task',
            name='content',
            field=models.TextField(db_index=True, help_text='Полное описание теста', verbose_name='Описание теста'),
        ),
        migrations.AlterField(
            model_name='task',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='Названия групп (классов) где проводится тест', to='main.Group', verbose_name='Группы (классы)'),
        ),
        migrations.AlterField(
            model_name='task',
            name='is_active',
            field=models.BooleanField(db_index=True, default=False, help_text='Отображение теста на сайте', verbose_name='Статус отображения'),
        ),
        migrations.AlterField(
            model_name='task',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tasks', to='main.Lesson', verbose_name='Предмет (урок)'),
        ),
    ]
