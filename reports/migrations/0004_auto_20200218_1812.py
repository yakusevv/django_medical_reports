# Generated by Django 2.2.7 on 2020-02-18 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_auto_20191012_1834'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pricegroup',
            options={'verbose_name': 'Price group', 'verbose_name_plural': 'Price groups'},
        ),
        migrations.AddField(
            model_name='service',
            name='price_doctor',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Price for the doctor'),
        ),
        migrations.AddField(
            model_name='serviceitem',
            name='service_price_doctor',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Service price for the doctor'),
        ),
        migrations.AddField(
            model_name='visittariff',
            name='price_doctor',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Price for the doctor'),
        ),
    ]