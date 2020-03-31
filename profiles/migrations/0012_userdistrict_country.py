# Generated by Django 3.0.4 on 2020-03-16 15:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0014_typeofvisit_short_name'),
        ('profiles', '0011_auto_20200316_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdistrict',
            name='country',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='user_district', to='reports.Country', verbose_name='Country'),
            preserve_default=False,
        ),
    ]