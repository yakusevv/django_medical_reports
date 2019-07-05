# Generated by Django 2.2.1 on 2019-07-04 19:07

from django.db import migrations, models
import django.db.models.deletion
import reports.models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=reports.models.get_image_path)),
                ('position', models.IntegerField()),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='additional_images', to='reports.Report')),
            ],
        ),
    ]
