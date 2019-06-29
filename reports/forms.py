from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from django.forms.models import BaseInlineFormSet

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

    def clean(self):
        cleaned_data=super(ReportCreateForm, self).clean()
#        for form in self.formset:
#            if not form.is_valid():
#                raise forms.ValidationError('some error')
        return cleaned_data

class ServiceItemForm(forms.ModelForm):

    class Meta:
        model = ServiceItem
        fields = [
            'service',
            'quantity'
            ]

class ServiceItemsFormset(BaseInlineFormSet):

    def clean(self):
        if any(self.errors):
            return
        services = set()
        number_of_forms = 0
        for form in self.forms:
            if form.cleaned_data:
                if not form.cleaned_data['DELETE']:
                    service = form.cleaned_data['service']
                    quantity = form.cleaned_data['quantity']
                    number_of_forms += 1
                    if service in services:
                        form.add_error('service','Duplicate values for "Service" are not allowed.')
                    else:
                        services.add(service)
                    if quantity < 1:
                        form.add_error('quantity', "Quantity must be equal to or greater than 1")
        if number_of_forms == 0:
            raise forms.ValidationError('At least one service must be chosen')


ServiceItemsFormSet = inlineformset_factory(
                    Report, ServiceItem, formset=ServiceItemsFormset,
                    form=ServiceItemForm, extra=1
                    )
