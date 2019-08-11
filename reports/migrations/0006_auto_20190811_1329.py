# Generated by Django 2.2.1 on 2019-08-11 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0005_auto_20190718_1715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='disease',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='pricegroup',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='kind_of_visit',
            field=models.CharField(choices=[('D', 'Standard day visit'), ('N', 'Night visit'), ('H', 'Holiday visit'), ('F', 'Family visit'), ('S', 'Second visit')], default='D', max_length=1),
        ),
    ]
