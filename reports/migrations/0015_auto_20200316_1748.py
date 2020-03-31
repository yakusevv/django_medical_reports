# Generated by Django 3.0.4 on 2020-03-16 16:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0014_typeofvisit_short_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reporttemplate',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Country', unique=True, verbose_name='Country'),
        ),
        migrations.AlterUniqueTogether(
            name='reporttemplate',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='reporttemplate',
            name='company',
        ),
    ]