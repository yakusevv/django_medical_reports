# Generated by Django 3.0.4 on 2020-03-09 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0011_auto_20200306_2344'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serviceitem',
            name='service_price',
        ),
        migrations.RemoveField(
            model_name='serviceitem',
            name='service_price_doctor',
        ),
        migrations.AddField(
            model_name='service',
            name='unsummable_price',
            field=models.BooleanField(default=False, verbose_name='Unsummable price'),
        ),
        migrations.AddField(
            model_name='serviceitem',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name='serviceitem',
            name='cost_doctor',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]
