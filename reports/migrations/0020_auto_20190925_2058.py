# Generated by Django 2.2.1 on 2019-09-25 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0019_auto_20190917_2136'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='location',
        ),
        migrations.AddField(
            model_name='profile',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='reports.City'),
        ),
        migrations.AlterField(
            model_name='disease',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.Country'),
        ),
        migrations.AlterField(
            model_name='service',
            name='country',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='services', to='reports.Country'),
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='reports.Service'),
        ),
        migrations.AlterField(
            model_name='tariff',
            name='price_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.PriceGroup'),
        ),
    ]
