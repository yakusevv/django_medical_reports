# Generated by Django 2.2.1 on 2019-08-22 22:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0010_auto_20190816_0028'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tariff',
            old_name='visit',
            new_name='type_of_visit',
        ),
        migrations.RenameModel(
            old_name='Visit',
            new_name='TypeOfVisit',
        ),
        migrations.CreateModel(
            name='VisitItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('tariff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Tariff')),
                ('type_of_visit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.TypeOfVisit')),
            ],
        ),
    ]
