# Generated by Django 3.0.4 on 2020-03-29 19:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0015_auto_20200327_1458'),
        ('reports', '0028_reportrequest_seen'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='company',
        ),
        migrations.RemoveField(
            model_name='report',
            name='ref_number',
        ),
        migrations.AddField(
            model_name='reportrequest',
            name='ref_number',
            field=models.CharField(default=0, max_length=6, verbose_name='Ref. number'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reportrequest',
            name='sender',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='profiles.Profile', verbose_name='Sender'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reportrequest',
            name='status',
            field=models.CharField(choices=[('accepted', 'Is accepted'), ('cancelled_by_company', 'Cancelled by company'), ('wrong_data', 'Wrong request data'), ('failed', 'The visit did not take place')], default='accepted', max_length=20),
        ),
        migrations.AlterField(
            model_name='report',
            name='report_request',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='reports.ReportRequest'),
        ),
        migrations.AlterField(
            model_name='reportrequest',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.Company', verbose_name='Company'),
        ),
        migrations.AlterField(
            model_name='reportrequest',
            name='doctor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='report_requests', to='profiles.Profile', verbose_name='Doctor'),
        ),
    ]
