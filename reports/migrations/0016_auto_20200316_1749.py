# Generated by Django 3.0.4 on 2020-03-16 16:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0015_auto_20200316_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reporttemplate',
            name='country',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='reports.Country', verbose_name='Country'),
        ),
    ]
