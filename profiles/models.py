from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.shortcuts import redirect

from reports.models import District, City


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    num_col = models.CharField(max_length=9, unique=True)
    districts = models.ManyToManyField(District)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return ' '.join((self.user.last_name, self.user.first_name, self.num_col))

    def get_absolute_url(self):
        return reverse('profile_detail_url', kwargs={'pk': self.pk})


class ProfileReportAutofillTemplate(models.Model):
    doctor = models.ForeignKey(Profile, related_name='report_templates', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    cause_of_visit_template =models.TextField(max_length=700, blank=True)
    checkup_template = models.TextField(max_length=1200, blank=True)
    additional_checkup_template = models.TextField(max_length=700, blank=True)
    prescription_template = models.TextField(max_length=700, blank=True)

    class Meta:
        unique_together = (('doctor','name',),)
        verbose_name = 'Report autofill template'
        verbose_name_plural = 'Report autofill templates'

    def get_update_url(self):
        return reverse('profile_template_update_url', kwargs={'pk': self.pk})
