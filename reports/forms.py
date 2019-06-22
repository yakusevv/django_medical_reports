from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory

from .models import Report, ServiceItem


class ReportCreateForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = [
            'ref_number',
            'company_ref_number',
            'company',
            'patients_first_name',
            'patients_last_name',
            'patients_date_of_birth',
            'patients_policy_number',
            'patients_passport_number',
            'date_of_visit',
            'location',
            'cause',
            'checkup',
            'additional_checkup',
            'second_visit',
            'diagnosis',
            'prescription',
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('doctor')
        super(ReportCreateForm, self).__init__(*args, **kwargs)

class ServiceItemForm(forms.ModelForm):

    class Meta:
        model = ServiceItem
        fields = [
            'service',
            'quantity'
            ]


ServiceItemsFormSet = inlineformset_factory(
                    Report, ServiceItem,
                    form=ServiceItemForm, extra=1)
