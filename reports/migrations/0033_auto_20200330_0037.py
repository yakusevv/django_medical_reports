# Generated by Django 3.0.4 on 2020-03-30 00:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0032_auto_20200330_0022'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='reportrequest',
            unique_together=set(),
        ),
    ]
