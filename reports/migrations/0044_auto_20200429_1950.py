# Generated by Django 3.0.4 on 2020-04-29 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0043_auto_20200427_2203'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='time_of_visit',
            field=models.TimeField(blank=True, null=True, verbose_name='Time of visit'),
        ),
        migrations.AlterField(
            model_name='report',
            name='date_of_visit',
            field=models.DateField(verbose_name='Date of visit'),
        ),
    ]
