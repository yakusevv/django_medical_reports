# Generated by Django 2.2.1 on 2019-10-12 16:34

from django.db import migrations, models
import django.db.models.deletion
import reports.models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_auto_20191005_2344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionalimage',
            name='image',
            field=models.ImageField(upload_to=reports.models.get_image_path, verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='additionalimage',
            name='position',
            field=models.IntegerField(verbose_name='Position'),
        ),
        migrations.AlterField(
            model_name='additionalimage',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='additional_images', to='reports.Report', verbose_name='Report'),
        ),
        migrations.AlterField(
            model_name='city',
            name='district',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.District', verbose_name='District'),
        ),
        migrations.AlterField(
            model_name='city',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=20, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='company',
            name='price_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.PriceGroup', verbose_name='Price group'),
        ),
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='disease',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.Country', verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='disease',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='district',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='district',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.Region', verbose_name='Region'),
        ),
        migrations.AlterField(
            model_name='pricegroup',
            name='name',
            field=models.CharField(max_length=50, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='region',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.Country', verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='region',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='report',
            name='additional_checkup',
            field=models.TextField(blank=True, max_length=700, verbose_name='Additional checkup'),
        ),
        migrations.AlterField(
            model_name='report',
            name='cause_of_visit',
            field=models.TextField(max_length=700, verbose_name='Cause of visit'),
        ),
        migrations.AlterField(
            model_name='report',
            name='checked',
            field=models.BooleanField(default=False, verbose_name='Is checked'),
        ),
        migrations.AlterField(
            model_name='report',
            name='checkup',
            field=models.TextField(max_length=1200, verbose_name='Checkup'),
        ),
        migrations.AlterField(
            model_name='report',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.City', verbose_name='City'),
        ),
        migrations.AlterField(
            model_name='report',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.Company', verbose_name='Company'),
        ),
        migrations.AlterField(
            model_name='report',
            name='company_ref_number',
            field=models.CharField(max_length=50, verbose_name='Company ref. number'),
        ),
        migrations.AlterField(
            model_name='report',
            name='date_of_visit',
            field=models.DateTimeField(verbose_name='Date of visit'),
        ),
        migrations.AlterField(
            model_name='report',
            name='detailed_location',
            field=models.CharField(blank=True, max_length=100, verbose_name='Detailed location'),
        ),
        migrations.AlterField(
            model_name='report',
            name='diagnosis',
            field=models.ManyToManyField(related_name='reports', to='reports.Disease', verbose_name='Diagnosis'),
        ),
        migrations.AlterField(
            model_name='report',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='profiles.Profile', verbose_name='Doctor'),
        ),
        migrations.AlterField(
            model_name='report',
            name='docx_download_link',
            field=models.CharField(blank=True, max_length=500, verbose_name='Download link'),
        ),
        migrations.AlterField(
            model_name='report',
            name='patients_date_of_birth',
            field=models.DateField(verbose_name='Date of birth'),
        ),
        migrations.AlterField(
            model_name='report',
            name='patients_first_name',
            field=models.CharField(max_length=50, verbose_name='First name'),
        ),
        migrations.AlterField(
            model_name='report',
            name='patients_last_name',
            field=models.CharField(max_length=50, verbose_name='Last name'),
        ),
        migrations.AlterField(
            model_name='report',
            name='patients_policy_number',
            field=models.CharField(blank=True, max_length=100, verbose_name='Policy number'),
        ),
        migrations.AlterField(
            model_name='report',
            name='prescription',
            field=models.TextField(max_length=700, verbose_name='Prescription'),
        ),
        migrations.AlterField(
            model_name='report',
            name='ref_number',
            field=models.CharField(max_length=50, verbose_name='Ref. number'),
        ),
        migrations.AlterField(
            model_name='report',
            name='type_of_visit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.TypeOfVisit', verbose_name='Type of visit'),
        ),
        migrations.AlterField(
            model_name='report',
            name='visit_price',
            field=models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Visit price'),
        ),
        migrations.AlterField(
            model_name='reporttemplate',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Company', verbose_name='Company'),
        ),
        migrations.AlterField(
            model_name='reporttemplate',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Country', verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='reporttemplate',
            name='template',
            field=models.FileField(storage=reports.models.OverwriteStorage(), upload_to=reports.models.get_docxtemplate_path, verbose_name='Template'),
        ),
        migrations.AlterField(
            model_name='service',
            name='country',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='services', to='reports.Country', verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='service',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='service',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='quantity',
            field=models.PositiveIntegerField(default=1, verbose_name='Quantity'),
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_items', to='reports.Report', verbose_name='Report'),
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='reports.Service', verbose_name='Service'),
        ),
        migrations.AlterField(
            model_name='serviceitem',
            name='service_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Service price'),
        ),
        migrations.AlterField(
            model_name='tariff',
            name='district',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.District', verbose_name='District'),
        ),
        migrations.AlterField(
            model_name='tariff',
            name='price_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.PriceGroup', verbose_name='Price group'),
        ),
        migrations.AlterField(
            model_name='typeofvisit',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.Country', verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='typeofvisit',
            name='is_second_visit',
            field=models.BooleanField(default=False, verbose_name='Is second visit'),
        ),
        migrations.AlterField(
            model_name='typeofvisit',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='visittariff',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='visittariff',
            name='tariff',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.Tariff', verbose_name='Tariff'),
        ),
        migrations.AlterField(
            model_name='visittariff',
            name='type_of_visit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reports.TypeOfVisit', verbose_name='Type of visit'),
        ),
    ]
