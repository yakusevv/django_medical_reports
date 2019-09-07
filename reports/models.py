import os

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse


def get_image_path(instance, filename):
    return os.path.join(
                    'FILES',
                    str(instance.report.company),
                    str(instance.report.doctor),
                    str(instance.report),
                    filename
                    )


class Country(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=50)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)

    def __str__(self):
        return ' - '.join((str(self.region), self.name))


class City(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=40, blank=True)
    num_col = models.CharField(max_length=9, unique=True)
    districts = models.ManyToManyField(District)

    def __str__(self):
        return ' '.join((self.user.last_name, self.user.first_name, self.num_col))

    def get_absolute_url(self):
        return reverse('user_profile_url', kwargs={'pk': self.user.pk})


# Every disease in reports must have a name in language of country where was visit
# so property "country" has been added
class Disease(models.Model):
    name = models.CharField(max_length=50, unique=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, default=1)

    def __str__(self):
        return self.name


class PriceGroup(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# Every country must have a list of visit types with appropriative names
class TypeOfVisit(models.Model):
    name = models.CharField(max_length=50, unique=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, default=1)

    def __str__(self):
        return self.name


class Tariff(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    price_group = models.ForeignKey(PriceGroup, on_delete=models.PROTECT)
#    type_of_visit = models.ForeignKey(TypeOfVisit, on_delete=models.PROTECT)
#    price = models.DecimalField(max_digits=8, decimal_places=2)
#    day_visit = models.DecimalField(max_digits=8, decimal_places=2)
#    night_visit = models.DecimalField(max_digits=8, decimal_places=2)
#    holiday_visit = models.DecimalField(max_digits=8, decimal_places=2)
#    family_visit = models.DecimalField(max_digits=8, decimal_places=2)
#    second_visit = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return ' - '.join((str(self.district), str(self.price_group)))


class VisitTariff(models.Model):
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE)
    type_of_visit = models.ForeignKey(TypeOfVisit, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return ' - '.join((str(self.tariff), str(self.type_of_visit)))


class Company(models.Model):
    name = models.CharField(max_length=20, unique=True)
    price_group = models.ForeignKey(PriceGroup, on_delete=models.PROTECT)
    #template = models.FileField()

    def __str__(self):
        return self.name


# Every company need to have templates for each country in appropriative language
# Not checked yet
#class ReportTemplate(models.Model):
#    template = models.FileField()
#    company = models.ForeignKey(Company, on_delete=models.CASCADE)
#    country = models.ForeignKey(Country, on_delete=models.CASCADE)


class Report(models.Model):

    ref_number = models.CharField(max_length=50)
    company_ref_number = models.CharField(max_length=50)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    patients_first_name = models.CharField(max_length=50)
    patients_last_name = models.CharField(max_length=50)
    patients_date_of_birth = models.DateField()
    patients_policy_number = models.CharField(max_length=100, blank=True)
    kind_of_visit = models.ForeignKey(TypeOfVisit, on_delete=models.PROTECT)
    visit_price = models.DecimalField(max_digits=8, decimal_places=2)
    date_of_visit = models.DateTimeField()
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    detailed_location = models.CharField(max_length=100, blank=True)
    cause_of_visit = models.TextField(max_length=700)
    checkup = models.TextField(max_length=1200)
    additional_checkup = models.TextField(max_length=500, blank=True)
    diagnosis = models.ManyToManyField('Disease', related_name='reports')
    prescription = models.TextField(max_length=500)
    checked = models.BooleanField(default=False)
    doctor = models.ForeignKey(Profile, on_delete=models.PROTECT)
    docx_download_link = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return ' '.join((self.ref_number, self.patients_last_name, self.patients_first_name))

    def get_absolute_url(self):
        return reverse('report_detail_url', kwargs={'pk': self.pk})

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Report._meta.fields]

    @property
    def get_total_price(self):
        total = 0
        services = self.service_items.get_queryset()
        for service in services:
            total += service.cost
        total += self.visit_price
        return total

    get_total_price.fget.short_description = 'Total price'

class AdditionalImage(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to=get_image_path)
    position = models.IntegerField(blank=False)


#    Every country has a list of services with prices for each.
class Service(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='services', default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2 )

    def __str__(self):
        return self.country.name + ' - ' + self.name


class ServiceItem(models.Model):
    report = models.ForeignKey(Report, related_name='service_items', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, related_name='items', on_delete=models.CASCADE)
    service_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        if self.quantity > 1:
            return str(self.service.name) + ' [{}]'.format(self.quantity)
        return self.service.name

    @property
    def cost(self):
        return self.service_price * self.quantity
