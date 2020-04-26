import datetime

from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from django.utils.translation import ugettext as _

from .models import ReportRequest, Company
from profiles.models import Profile


class ReportRequestSerializer(serializers.ModelSerializer):
    STATUS = (
        ('cancelled_by_company', _('Cancelled by company')),
        ('wrong_data', _('Wrong request data')),
        )

    doctor = serializers.PrimaryKeyRelatedField(
                                        queryset=Profile.objects.all(),
                                        )
    doctor_initials = serializers.CharField(source='doctor.initials', read_only=True)
    company = serializers.PrimaryKeyRelatedField(
                                        queryset=Company.objects.all()
                                        )
    company_name = serializers.CharField(source='company.name', read_only=True)
    date_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    seen = serializers.BooleanField(read_only=True)
    ref_number = serializers.IntegerField(required=False)
    sender_initials = serializers.CharField(source='sender.initials', read_only=True)
    status = serializers.ChoiceField(choices=STATUS, required=False)

    class Meta:
        model = ReportRequest
        fields = [
                  'doctor',
                  'doctor_initials',
                  'company',
                  'company_name',
                  'message',
                  'date_time',
                  'pk',
                  'seen',
                  'ref_number',
                  'sender_initials',
                  'status',
        ]


class CompanyOptionsSerializer(serializers.ModelSerializer):
    ref_number_next = serializers.SerializerMethodField(read_only=True)

    def get_ref_number_next(self, obj):
        year = datetime.datetime.now().year
        company = obj

        country = self.context.get('user').profile.city.district.region.country
        largest = ReportRequest.objects.filter(doctor__city__district__region__country=country,
                                               company=company,
                                               date_time__year=year
                                               )
        if not largest:
            largest = 1
        else:
            largest = largest.order_by('ref_number').last().ref_number + 1
        return largest

    class Meta:
        model = Company
        fields = ['pk', 'name', 'ref_number_next']


class DoctorOptionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['pk', 'initials']
