# Generated by Django 3.0.8 on 2020-07-23 10:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_remove_exam_tasks'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='date_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
