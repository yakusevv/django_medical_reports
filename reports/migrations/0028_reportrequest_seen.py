# Generated by Django 3.0.4 on 2020-03-28 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0027_auto_20200326_2123'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportrequest',
            name='seen',
            field=models.BooleanField(default=False),
        ),
    ]
