# Generated by Django 3.0.4 on 2020-03-16 01:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0014_typeofvisit_short_name'),
        ('profiles', '0009_auto_20200315_2033'),
    ]

    operations = [
        migrations.AddField(
            model_name='profilereportautofilltemplate',
            name='country',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='report_templates', to='reports.Country', verbose_name='Country'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='profilereportautofilltemplate',
            name='diagnosis_template',
            field=models.ManyToManyField(related_name='autofill_template', to='reports.Disease', verbose_name='Diagnosis'),
        ),
    ]
