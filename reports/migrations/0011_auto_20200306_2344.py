# Generated by Django 2.2.7 on 2020-03-06 22:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0010_remove_report_docx_download_link'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='report',
            unique_together=set(),
        ),
    ]
