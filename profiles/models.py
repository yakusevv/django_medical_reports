from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from reports.models import District, City


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("User"))
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, verbose_name=_("City"))
    num_col = models.CharField(max_length=9, unique=True, verbose_name=_("Num. col"))
    districts = models.ManyToManyField(District, verbose_name=_("District"))

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return ' '.join((self.user.last_name, self.user.first_name, self.num_col))

    def get_absolute_url(self):
        return reverse('profile_detail_url', kwargs={'pk': self.pk})


class ProfileReportAutofillTemplate(models.Model):
    doctor = models.ForeignKey(Profile, related_name='report_templates', on_delete=models.CASCADE, verbose_name=_("Doctor"))
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    cause_of_visit_template =models.TextField(max_length=700, blank=True, verbose_name=_("Cause of visit"))
    checkup_template = models.TextField(max_length=1200, blank=True, verbose_name=_("Checkup"))
    additional_checkup_template = models.TextField(max_length=700, blank=True, verbose_name=_("Additional checkup"))
    prescription_template = models.TextField(max_length=700, blank=True, verbose_name=_("Prescription"))

    class Meta:
        unique_together = (('doctor','name',),)
        verbose_name = _('Report autofill template')
        verbose_name_plural = _('Report autofill templates')

    def get_update_url(self):
        return reverse('profile_template_update_url', kwargs={'pk': self.pk})
