# Generated by Django 2.2.7 on 2020-02-18 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0006_auto_20200218_1926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceitem',
            name='service_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Service price'),
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='service_price_doctor',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Service price for the doctor'),
        ),
    ]
