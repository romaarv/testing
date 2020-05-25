# Generated by Django 3.0.6 on 2020-05-25 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20200525_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advuser',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active'),
        ),
    ]
