from rest_framework import serializers

from .models import ReportRequest, Company
from profiles.models import Profile


class ReportRequestSerializer(serializers.HyperlinkedModelSerializer):
    doctor = serializers.SlugRelatedField(
                                        slug_field='id',
                                        queryset=Profile.objects.all()
                                        )
    company = serializers.SlugRelatedField(
                                        slug_field='id',
                                        queryset=Company.objects.all()
                                        )
    date_time = serializers.DateTimeField(read_only=True, format='%d-%m-%Y %H:%M:%S')

    class Meta:
        model = ReportRequest
        fields = ['doctor', 'company', 'message', 'date_time']
