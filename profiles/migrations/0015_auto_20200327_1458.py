# Generated by Django 3.0.4 on 2020-03-27 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0014_profile_viber_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='viber_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='Viber id'),
        ),
    ]
