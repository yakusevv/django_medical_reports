# Generated by Django 3.0.4 on 2020-03-12 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0012_auto_20200309_1952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disease',
            name='name',
            field=models.CharField(max_length=80, unique=True, verbose_name='Name'),
        ),
    ]
