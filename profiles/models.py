from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse

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
        return reverse('profile_detail_url', kwargs={'pk': self.user.profile.pk})
