# Generated by Django 3.0.8 on 2020-08-02 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20200727_0149'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='name_en',
            field=models.CharField(db_index=True, help_text='Название класса или группы', max_length=100, null=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='group',
            name='name_ru',
            field=models.CharField(db_index=True, help_text='Название класса или группы', max_length=100, null=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='group',
            name='name_uk',
            field=models.CharField(db_index=True, help_text='Название класса или группы', max_length=100, null=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='name_en',
            field=models.CharField(db_index=True, help_text='Предмет, знания которого проверяются в тесте', max_length=100, null=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='name_ru',
            field=models.CharField(db_index=True, help_text='Предмет, знания которого проверяются в тесте', max_length=100, null=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='name_uk',
            field=models.CharField(db_index=True, help_text='Предмет, знания которого проверяются в тесте', max_length=100, null=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='question',
            name='variant',
            field=models.PositiveIntegerField(db_index=True, default=1, help_text='При создании нескольких вариантов теста', verbose_name='Вариант'),
        ),
    ]
