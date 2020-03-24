from rest_framework import serializers

from .models import ReportRequest, Company
from profiles.models import Profile


class ReportRequestSerializer(serializers.HyperlinkedModelSerializer):
    doctor = serializers.PrimaryKeyRelatedField(
                                        queryset=Profile.objects.all(),
                                        )
    doctor_initials = serializers.CharField(source='doctor.initials', read_only=True)
    company = serializers.PrimaryKeyRelatedField(
                                        queryset=Company.objects.all()
                                        )
    company_name = serializers.CharField(source='company.name', read_only=True)
    date_time = serializers.DateTimeField(read_only=True, format='%d-%m-%Y %H:%M:%S')

    class Meta:
        model = ReportRequest
        fields = ['doctor', 'doctor_initials', 'company', 'company_name', 'message', 'date_time', 'pk']


class CompanyOptionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ['pk', 'name']


class DoctorOptionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['pk', 'initials']