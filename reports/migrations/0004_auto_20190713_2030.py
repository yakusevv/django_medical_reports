# Generated by Django 2.2.1 on 2019-07-13 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_report_docx_download_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='docx_download_link',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
