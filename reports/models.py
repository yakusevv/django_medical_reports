from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=40, blank=True)
    num_col = models.CharField(max_length=9, unique=True)

    def __str__(self):
        return self.user.last_name + ' ' + self.user.first_name + ' ' + self.num_col

    def get_absolute_url(self):
        return reverse('user_profile_url', kwargs={'pk': self.user.pk})

class Company(models.Model):
    name = models.CharField(max_length=20, unique=True)
    #template = models.FileField()

    def __str__(self):
        return self.name

class Patient(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    policy_number = models.CharField(max_length=100)
    passport_number = models.CharField(max_length=100, unique=True)
    last_update = models.DateField(auto_now=True)
    #policy_image = models.ImageField()
    #passport_image = models.ImageField()

    def __str__(self):
        return self.last_name + ' ' + self.first_name + ' ' + self.date_of_birth

#class PatientAdditionalImages(models.Model):
    #image = models.ImageField()
    #patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='additional_images')

class Report(models.Model):
    ref_number = models.CharField(max_length=50)
    company_ref_number = models.CharField(max_length=50)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    date_of_visit = models.DateTimeField()
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    location = models.CharField(max_length=100)
    cause = models.TextField(max_length=700)
    checkup = models.TextField(max_length=1200)
    additional_checkup = models.TextField(max_length=500, blank=True)
    second_visit = models.BooleanField(default=False)
    diagnosis = models.ManyToManyField('Disease', related_name='reports')
    prescription = models.TextField(max_length=500)
    checked = models.BooleanField(default=False)
    doctor = models.ForeignKey(Profile, on_delete=models.PROTECT)

    def __str__(self):
        return self.ref_number + ' ' + self.patient.last_name + ' ' + self.patient.first_name


class Disease(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Summary(models.Model):
    report = models.ForeignKey(Report, related_name='Summary', on_delete=models.CASCADE)


class Service(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2 )

    def __str__(self):
        return self.name


class ServiceItem(models.Model):
    summary = models.ForeignKey(Summary, related_name='items', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, related_name='service_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)

    @property
    def cost(self):
        return self.service.price * self.quantity
