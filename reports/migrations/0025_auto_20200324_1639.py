# Generated by Django 3.0.4 on 2020-03-24 16:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0024_auto_20200321_1827'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reportrequest',
            name='report',
        ),
        migrations.AddField(
            model_name='report',
            name='report_request',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reports.ReportRequest'),
        ),
    ]