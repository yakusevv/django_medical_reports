from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from reports.models import District, City, TypeOfVisit


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("User"))
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, verbose_name=_("City"))
    num_col = models.CharField(max_length=9, unique=True, verbose_name=_("Num. col"))
#    districts = models.ManyToManyField(District, verbose_name=_("District"))

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return ' '.join((self.user.last_name, self.user.first_name, self.num_col))

    def get_absolute_url(self):
        return reverse('profile_detail_url', kwargs={'pk': self.pk})


class ProfileReportAutofillTemplate(models.Model):
    doctor = models.ForeignKey(Profile, related_name='report_templates', on_delete=models.CASCADE, verbose_name=_("Doctor"))
    country = models.ForeignKey('reports.Country', related_name='report_templates', on_delete=models.CASCADE, verbose_name=_("Country"))
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    cause_of_visit_template =models.TextField(max_length=700, blank=True, verbose_name=_("Cause of visit"))
    checkup_template = models.TextField(max_length=1200, blank=True, verbose_name=_("Checkup"))
    additional_checkup_template = models.TextField(max_length=700, blank=True, verbose_name=_("Additional checkup"))
    prescription_template = models.TextField(max_length=700, blank=True, verbose_name=_("Prescription"))
    diagnosis_template = models.ManyToManyField('reports.Disease', related_name='autofill_template', verbose_name=_("Diagnosis"), blank=True)

    class Meta:
        unique_together = (('doctor','name',),)
        verbose_name = _('Report autofill template')
        verbose_name_plural = _('Report autofill templates')

    def get_update_url(self):
        return reverse('profile_template_update_url', kwargs={'pk': self.pk})


class UserDistrict(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
#    district = models.ForeignKey(District, on_delete=models.CASCADE, verbose_name=_("District"))
    cities = models.ManyToManyField('reports.City', related_name='cities', verbose_name=_("Cities"))
    country = models.ForeignKey('reports.Country', related_name='user_district', verbose_name=_("Country"), on_delete=models.CASCADE)

    class Meta:
#        unique_together = (('user', 'district'),)
        verbose_name = _('District coverage')
        verbose_name_plural = _('Districts coverage')

    def __str__(self):
        return ' - '.join((str(self.user.profile), 'district', str(str(self.cities.all()[0].name) + '...')))


class UserDistrictVisitPrice(models.Model):
    user_district = models.ForeignKey(UserDistrict, on_delete=models.CASCADE, verbose_name=_("District"))
    type_of_visit = models.ForeignKey(TypeOfVisit, on_delete=models.CASCADE, verbose_name=_("Type of visit"))
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("Price"))

    class Meta:
        unique_together = (('user_district', 'type_of_visit'),)
        verbose_name = _('Visit price for the doctor')
        verbose_name_plural = _('Visit prices for the doctors')

    def __str__(self):
        return ' - '.join((str(self.user_district), str(self.type_of_visit)))
