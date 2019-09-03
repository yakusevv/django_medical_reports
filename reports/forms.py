from django.core.files import File
from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from django.forms.models import BaseInlineFormSet

from .models import Report, ServiceItem, AdditionalImage, TypeOfVisit


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
            'date_of_visit',
            'kind_of_visit',
            'city',
            'detailed_location',
            'cause_of_visit',
            'checkup',
            'additional_checkup',
            'diagnosis',
            'prescription',
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('doctor')
        super(ReportCreateForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data=super(ReportCreateForm, self).clean()
        ref_number = cleaned_data.get("ref_number")
        first_name = cleaned_data.get("patients_first_name")
        last_name = cleaned_data.get("patients_last_name")
        if Report.objects.filter(ref_number=ref_number).filter(patients_last_name=last_name).filter(patients_first_name=first_name).exists():
            msg = "Report with this name is already exist"
            self.add_error('ref_number', msg)
            self.add_error('patients_first_name', msg)
            self.add_error('patients_last_name', msg)
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


class AdditionalImageForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput(attrs={'multiple': True}), required=True)

    class Meta:
        model = AdditionalImage
        fields = ['image']


    def save(self, *args, **kwargs):
        file_list = self.files.getlist('image')
        position = 1
        for file in file_list:
            inst = AdditionalImage(
                report=self.instance.report,
                image=file,
                position=position
            )
            inst.save()
            position += 1


class VisitTariffInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        if kwargs['instance'].pk:
            current_instances = [inst.type_of_visit.pk for inst in kwargs['instance'].visittariff_set.all()]
            type_of_visit_filtered = TypeOfVisit.objects.filter(
                        country=kwargs['instance'].district.region.country
        ).exclude(
                        pk__in=current_instances
                 )
            kwargs['initial'] = [
            {'type_of_visit': type.id, 'price': '-'} for type in type_of_visit_filtered
        ]
        super(VisitTariffInlineFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            type_of_visit_field = form.fields['type_of_visit']
            type_of_visit_field.widget.attrs = {'readonly':'readonly'}
            type_of_visit_field.widget.can_add_related = False
            type_of_visit_field.widget.can_change_related = False
            type_of_visit_field.disabled =  True

    def clean(self):
        for form in self.forms:
            try:
                if form.cleaned_data.get('price'):
                    price = form.cleaned_data.get('price')
                    if int(price) < 0:
                        form.add_error('price', 'The Price can\'t be less than 0')
                elif form.cleaned_data.get('price') == 0:
                    form.add_error('price', 'The Price can\'t be 0')
            except ValueError:
                form.add_error('price', 'The Price should be numeric type')
