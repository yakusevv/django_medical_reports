from rest_framework import serializers

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
    date_time = serializers.DateTimeField(read_only=True, format='%d-%m-%Y %H:%M:%S')
    seen = serializers.BooleanField(read_only=True)
    ref_number = serializers.IntegerField(read_only=True)
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
                  'status'
        ]


class CompanyOptionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ['pk', 'name']


class DoctorOptionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['pk', 'initials']
