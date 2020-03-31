# Generated by Django 3.0.4 on 2020-03-16 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0014_typeofvisit_short_name'),
        ('profiles', '0010_auto_20200316_0221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilereportautofilltemplate',
            name='diagnosis_template',
            field=models.ManyToManyField(blank=True, related_name='autofill_template', to='reports.Disease', verbose_name='Diagnosis'),
        ),
    ]