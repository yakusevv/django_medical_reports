# Generated by Django 3.0.4 on 2020-03-29 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0029_auto_20200329_1905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportrequest',
            name='ref_number',
            field=models.IntegerField(max_length=6, verbose_name='Ref. number'),
        ),
    ]