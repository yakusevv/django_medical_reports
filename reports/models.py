import os
import shutil

from django.db import models
from django.shortcuts import reverse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def get_image_path(instance, filename):
    return os.path.join(
                    'FILES',
                    str(instance.report.pk),
                    filename
                    )


def get_docxtemplate_path(instance, filename):
    filename = str(instance.country.name) + '_template.docx'
    return os.path.join('DOC_TEMPLATES', filename)


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return name


class Country(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Name"))

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name=_("Country"))

    class Meta:
        unique_together = (('name', 'country',),)
        verbose_name = _('Region')
        verbose_name_plural = _('Regions')

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    region = models.ForeignKey(Region, on_delete=models.PROTECT, verbose_name=_("Region"))

    class Meta:
        unique_together = (('name', 'region',),)
        verbose_name = _('District')
        verbose_name_plural = _('Districts')

    def __str__(self):
        return ' - '.join((str(self.region), self.name))


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    district = models.ForeignKey(District, on_delete=models.PROTECT, verbose_name=_("District"))

    class Meta:
        unique_together = (('name', 'district',),)
        verbose_name = _('City')
        verbose_name_plural = _('Cities')

    def __str__(self):
        return ' - '.join((str(self.name), str(self.district.region.country)))

    def validate_unique(self, exclude=None):
        qs = City.objects.filter(district__region__country=self.district.region.country)
        if self.pk is None:
            if qs.filter(name=self.name).exists():
                raise ValidationError(_("City with this name in the current country is already exists"))

    def save(self, *args, **kwargs):
        self.validate_unique()
        super(City, self).save(*args, **kwargs)



# Every disease in reports must have a name in language of country where was visit
# so property "country" has been added
class Disease(models.Model):
    name = models.CharField(max_length=80, unique=True, verbose_name=_("Name"))
    country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name=_("Country"))

    class Meta:
        verbose_name = _('Disease')
        verbose_name_plural = _('Diseases')

    def __str__(self):
        return self.name


class PriceGroup(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Name"))

    class Meta:
        verbose_name = _('Price group')
        verbose_name_plural = _('Price groups')

    def __str__(self):
        return self.name


# Every country must have a list of visit types with appropriative names
class TypeOfVisit(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    short_name = models.CharField(max_length=50, verbose_name=_("Short name"), blank=True)
    is_second_visit = models.BooleanField(default=False, verbose_name=_("Is second visit"))
    country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name=_("Country"))
    initial = models.CharField(max_length=2, verbose_name=_("Initial"), blank=True)

    class Meta:
        unique_together = (('name', 'country',))
        verbose_name = _('Type of visit')
        verbose_name_plural = _('Types of visits')

    def __str__(self):
        return self.name


class Tariff(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, verbose_name=_("District"))
    price_group = models.ForeignKey(PriceGroup, on_delete=models.CASCADE, verbose_name=_("Price group"))

    class Meta:
        unique_together = (('district', 'price_group',),)
        verbose_name = _('Tariff')
        verbose_name_plural = _('Tariffs')
        ordering = ('price_group',)

    def __str__(self):
        return ' - '.join((str(self.district), str(self.price_group)))


class VisitTariff(models.Model):
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, verbose_name=_("Tariff"))
    type_of_visit = models.ForeignKey(TypeOfVisit, on_delete=models.CASCADE, verbose_name=_("Type of visit"))
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Price"))
#    price_doctor = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name=_("Price for the doctor"))

    class Meta:
        unique_together = (('tariff', 'type_of_visit',),)
        verbose_name = _('Visit tariff')
        verbose_name_plural = _('Visit tariffs')

    def __str__(self):
        return ' - '.join((str(self.tariff), str(self.type_of_visit)))


class Company(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name=_("Name"))
    price_group = models.ForeignKey(PriceGroup, on_delete=models.PROTECT, verbose_name=_("Price group"))
    initials = models.CharField(max_length=3, verbose_name=_("Initials"), blank=True)

    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')

    def __str__(self):
        return self.name


# Every country need to have template in appropriative language
class ReportTemplate(models.Model):
    template = models.FileField(upload_to=get_docxtemplate_path, storage=OverwriteStorage(), verbose_name=_("Template"))
#    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name=_("Company"))
    country = models.OneToOneField(Country, on_delete=models.CASCADE, verbose_name=_("Country"))

    class Meta:
#        unique_together = (('company', 'country',),)
        verbose_name = _('Report template')
        verbose_name_plural = _('Report templates')


class Report(models.Model):
#    ref_number = models.CharField(max_length=6, verbose_name=_("Ref. number"))
    company_ref_number = models.CharField(max_length=50, verbose_name=_("Company ref. number"))
#    company = models.ForeignKey(Company, on_delete=models.PROTECT, verbose_name=_("Company"))
    patients_first_name = models.CharField(max_length=50, verbose_name=_("First name"))
    patients_last_name = models.CharField(max_length=50, verbose_name=_("Last name"))
    patients_date_of_birth = models.DateField(verbose_name=_("Date of birth"))
    patients_policy_number = models.CharField(max_length=100, blank=True, verbose_name=_("Policy number"))
    type_of_visit = models.ForeignKey(TypeOfVisit, on_delete=models.PROTECT, verbose_name=_("Type of visit"))
    visit_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Visit price"), default=0)
    visit_price_doctor = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Visit price for the doctor"), default=0)
    date_of_visit = models.DateTimeField(verbose_name=_("Date of visit"))
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name=_("City"))
    detailed_location = models.CharField(max_length=100, blank=True, verbose_name=_("Detailed location"))
    cause_of_visit = models.TextField(max_length=700, verbose_name=_("Cause of visit"))
    checkup = models.TextField(max_length=1200, verbose_name=_("Checkup"))
    additional_checkup = models.TextField(max_length=700, blank=True, verbose_name=_("Additional checkup"))
    diagnosis = models.ManyToManyField('Disease', related_name='reports', verbose_name=_("Diagnosis"))
    prescription = models.TextField(max_length=700, verbose_name=_("Prescription"))
    checked = models.BooleanField(default=False, verbose_name=_("Is checked"))
    doctor = models.ForeignKey('profiles.Profile', on_delete=models.PROTECT, verbose_name=_("Doctor"))
    report_request = models.OneToOneField('ReportRequest', on_delete=models.PROTECT, related_name='report')

    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')
        permissions = (
            ("can_download_excel", _("Can download excel")),
            )


#    def validate_unique(self, *args, **kwargs):
#        super(Report, self).validate_unique(*args, **kwargs)
#        current_year = self.date_of_visit.year
#        reports = self.__class__.objects.filter(
#                    city__district__region__country=self.city.district.region.country,
#                    date_of_visit__year=current_year
#                    ).exclude(pk=self.pk)
#        if reports:
#            for report in reports:
#                if report.company == self.company and report.ref_number == self.ref_number:
#                    raise ValidationError(
 #                       message=_('Report with this data is already exists.'),
 #                       code='unique_together',
 #                       )

    def __str__(self):
        return ' '.join((self.patients_last_name, self.patients_first_name, self.get_full_ref_number))

    def get_absolute_url(self):
        return reverse('report_detail_url', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('report_update_url', kwargs={'pk': self.pk})

    def get_images_update_url(self):
        return reverse('report_images_update_url', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('report_delete_url', kwargs={'pk': self.pk})

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Report._meta.fields]

    @property
    def get_total_price(self):
        total = 0
        if self.pk:
            services = self.service_items.get_queryset()
            for service in services:
                total += service.cost
            total += self.visit_price
            return total
        return total

    @property
    def get_total_price_doctor(self):
        total = 0
        if self.pk:
            services = self.service_items.get_queryset()
            for service in services:
                total += service.cost_doctor
            total += self.visit_price_doctor
            return total
        return total

    @property
    def get_full_ref_number(self):
        ref = str(self.report_request.company.initials) + str(self.report_request.ref_number).zfill(2)
        date_of_visit = str(self.report_request.date_time.strftime("%d%m"))
        if not self.doctor.is_foreign_doctor:
            info = self.doctor.initials + self.type_of_visit.initial
        else:
            info = self.doctor.initials
        return '-'.join((ref, date_of_visit, info))

    get_full_ref_number.fget.short_description = _('Full ref. number')
    get_total_price.fget.short_description = _('Total price')
    get_total_price_doctor.fget.short_description = _('Total price for the doctor')


class AdditionalImage(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='additional_images', verbose_name=_("Report"))
    image = models.ImageField(upload_to=get_image_path, verbose_name=_("Image"))
    position = models.IntegerField(blank=False, verbose_name=_("Position"))

    class Meta:
        verbose_name = _('Additional Image')
        verbose_name_plural = _('Additional Images')


#    Every country has a list of services with prices for each.
class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='services', default=1, verbose_name=_("Country"))
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Price"))
    price_doctor = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Price for the doctor"))
    unsummable_price = models.BooleanField(default=False, verbose_name=_('Unsummable price'))

    class Meta:
        unique_together = (('name', 'country',),)
        verbose_name = _('Service')
        verbose_name_plural = _('Services')

    def __str__(self):
        return self.country.name + ' - ' + self.name


class ServiceItem(models.Model):
    report = models.ForeignKey(Report, related_name='service_items', on_delete=models.CASCADE, verbose_name=_("Report"))
    service = models.ForeignKey(Service, related_name='items', on_delete=models.PROTECT, verbose_name=_("Service"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantity"))
    cost = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name=_("Cost"))
    cost_doctor = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name=_("Cost doctor"))

    class Meta:
        unique_together = (('report', 'service',),)
        verbose_name = _('Service item')
        verbose_name_plural = _('Service items')

    def __str__(self):
        if self.quantity > 1:
            return str(self.service.name) + ' [{}]'.format(self.quantity)
        return self.service.name


class ReportRequest(models.Model):
    STATUS = (
        ('accepted', _('Is accepted')),
        ('cancelled_by_company', _('Cancelled by company')),
        ('wrong_data', _('Wrong request data')),
        ('failed', _('The visit did not take place')),
    )

    doctor = models.ForeignKey(
                                'profiles.Profile',
                                on_delete=models.PROTECT,
                                verbose_name=_("Doctor"),
                                related_name="report_requests",
                                blank=True
                                )
    date_time = models.DateTimeField(verbose_name=_("Date and time"))
    company = models.ForeignKey('Company', on_delete=models.CASCADE, verbose_name=_("Company"))
    message = models.TextField(max_length=500, verbose_name=_("Message"))
    seen = models.BooleanField(default=False)
    ref_number = models.IntegerField(verbose_name=_("Ref. number"))
    company = models.ForeignKey(Company, on_delete=models.PROTECT, verbose_name=_("Company"))
    sender = models.ForeignKey('profiles.Profile', on_delete=models.PROTECT, verbose_name=_('Sender'))
    status = models.CharField(max_length=20, choices=STATUS, default='accepted')

 #   class Meta:
#        unique_together = (('doctor', 'ref_number', 'company'),)

    def validate_unique(self, exclude=None):
        country = self.doctor.city.district.region.country
        qs = ReportRequest.objects.filter(
                                            doctor__city__district__region__country=country,
                                            company=self.company,
                                            ref_number=self.ref_number,
                                            date_time__year=self.date_time.year
                                         )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(_("Case {}{} is already exists".format(
                                                                    self.company.initials,
                                                                    str(self.ref_number).zfill(3))
                                ))

    def save(self, *args, **kwargs):
        self.validate_unique()
        super(ReportRequest, self).save(*args, **kwargs)

    def __str__(self):
        return ' '.join((
                        str(self.company.initials),
                        str(self.ref_number).zfill(3),
                        str(' '.join(self.message.split()[:2])),
                        str(self.date_time.strftime('%d.%m.%Y %H:%M')),
                        str(self.doctor.initials)
                        ))

    def has_report(self):
        return hasattr(self, 'report') and self.report is not None

@receiver(post_delete, sender=Report)
def submission_delete(sender, instance, **kwargs):
    shutil.rmtree(
                str(os.path.join(
                        settings.MEDIA_ROOT,
                        'FILES',
                        str(instance.pk)
                        )
                    ), ignore_errors=True
                )


@receiver(pre_save, sender=AdditionalImage)
def image_update(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_image = AdditionalImage.objects.get(pk=instance.pk).image
            os.remove(old_image.path)
        except AdditionalImage.DoesNotExist:
            pass


@receiver(post_delete, sender=AdditionalImage)
def image_delete(sender, instance, **kwargs):
    try:
        os.remove(instance.image.path)
    except OSError:
        pass


@receiver(post_delete, sender=ReportTemplate)
def template_delete(sender, instance, **kwargs):
    os.remove(instance.template.path)


#viber messages
from .utils import send_text   # - to avoid circular import


def send_new_case_message(instance):
    viber_id = instance.doctor.viber_id
    message = "--- New Case for {} ---\n{}{} - {}\n{}".format(
        instance.doctor.initials,
        instance.company.initials,
        str(instance.ref_number).zfill(3),
        instance.date_time.strftime("%d.%m.%Y - %H:%M:%S"),
        instance.message
    )
    if viber_id:
        send_text(viber_id, message)


def send_update_case_message(instance):
    viber_id = instance.doctor.viber_id
    message = "--- Updated ---\n{}{} - {}\n{}".format(
        instance.company.initials,
        str(instance.ref_number).zfill(3),
        instance.date_time.strftime("%d.%m.%Y - %H:%M:%S"),
        instance.message
    )
    if viber_id:
        send_text(viber_id, message)


def send_cancel_case_message(instance):
    viber_id = instance.doctor.viber_id
    message = "--- Cancelled ---\n{}{} - {}".format(
        instance.company.initials,
        str(instance.ref_number).zfill(3),
        instance.date_time.strftime("%d.%m.%Y - %H:%M:%S")
    )
    if viber_id:
        send_text(viber_id, message)


@receiver(pre_save, sender=ReportRequest)
def report_request_save_change(sender, instance, **kwargs):
    if instance.pk and instance.status == 'accepted':
        prev_instance = ReportRequest.objects.get(pk=instance.pk)
        if prev_instance.doctor != instance.doctor:
            instance.seen = False
            send_new_case_message(instance)
            send_cancel_case_message(prev_instance)

        elif prev_instance.message != instance.message or prev_instance.company != instance.company:
            send_update_case_message(instance)

    elif instance.status == 'accepted':
        send_new_case_message(instance)
    elif instance.status == 'cancelled_by_company' and not instance.has_report():
        send_cancel_case_message(instance)

'''
@receiver(post_delete, sender=ReportRequest)
def report_request_delete(sender, instance, **kwargs):
    viber_id = instance.doctor.viber_id
    message = "--- Cancelled ---\n{} - {}".format(
        instance.company,
        instance.date_time.strftime("%d.%m.%Y - %H:%M:%S"),
    )
    if viber_id:
        send_text(viber_id, message)
'''