# Generated by Django 3.0.4 on 2020-03-30 01:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0015_auto_20200327_1458'),
        ('reports', '0033_auto_20200330_0037'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='reportrequest',
            unique_together={('doctor', 'ref_number', 'company')},
        ),
    ]
