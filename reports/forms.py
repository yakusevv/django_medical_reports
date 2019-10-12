from django.core.files import File
from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from django.forms.models import BaseInlineFormSet
from django.utils.translation import gettext_lazy as _

from tempus_dominus.widgets import DateTimePicker, DatePicker
from django_select2.forms import Select2MultipleWidget, Select2Widget

from .models import (
                    Report,
                    Service,
                    ServiceItem,
                    AdditionalImage,
                    TypeOfVisit,
                    VisitTariff,
                    Tariff,
                    Country
                    )


class ReportForm(forms.ModelForm):

    class Meta:
        model = Report
        exclude = [
            'visit_price',
            'checked',
            'doctor',
            'docx_download_link'
                  ]
        widgets = {
                   'diagnosis'    : Select2MultipleWidget,
                   'city'         : Select2Widget,
                   'company'      : Select2Widget,
                   'type_of_visit': Select2Widget,
                   'date_of_visit': DateTimePicker(
                                        options={
                                            'useCurrent': True,
                                            'format': 'DD/MM/YYYY HH:mm',
                                            },
                                        attrs={
                                            'append': 'fa fa-calendar',
                                            'icon_toggle': True,
                                            'size': 'small'
                                            }
                                    ),
                   'patients_date_of_birth': DatePicker(
                                        options={
                                            'useCurrent': True,
                                            'format': 'DD/MM/YYYY',
                                            'viewMode': 'years'
                                            },
                                        attrs={
                                            'append': 'fa fa-calendar',
                                            'icon_toggle': True,
                                            'size': 'small',
                                            }
                                    ),
                   }

    def clean(self):
        cleaned_data=super(ReportForm, self).clean()
        ref_number = cleaned_data.get("ref_number")
        first_name = cleaned_data.get("patients_first_name")
        last_name = cleaned_data.get("patients_last_name")
        same_reports = Report.objects.filter(
                            ref_number=ref_number
                        ).filter(
                            patients_last_name=last_name
                        ).filter(
                            patients_first_name=first_name
                        )
        if not self.instance.pk:
            if same_reports.exists():
                msg = _("Report with this name is already exist")
                self.add_error('ref_number', msg)
                self.add_error('patients_first_name', msg)
                self.add_error('patients_last_name', msg)
        else:
            same_reports = same_reports.exclude(pk=self.instance.pk)
            if len(same_reports) > 0:
                msg = _("Other report with this name is already exist")
                self.add_error('ref_number', msg)
                self.add_error('patients_first_name', msg)
                self.add_error('patients_last_name', msg)
        return cleaned_data


class ServiceItemForm(forms.ModelForm):

    class Meta:
        model = ServiceItem
        fields = [
            'service',
            'quantity',
            'service_price',
            ]
        widgets = {
                   'service_price': forms.HiddenInput(attrs={}),
                   'service'      : Select2Widget
                   }

    def __init__(self, *args, **kwargs):
        super(ServiceItemForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['service'].disabled = True

    def clean(self):
        cleaned_data = super(ServiceItemForm, self).clean()
        if self.instance.id and cleaned_data.get('service', False):
            if cleaned_data['DELETE']:
                self.instance.delete()
        if cleaned_data.get('service', False):
            service = cleaned_data['service']
            cleaned_data['service_price'] = Service.objects.get(pk=service.pk).price
        return cleaned_data


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
                        msg = _('Duplicate values for "Service" are not allowed.')
                        form.add_error('service', msg)
                    else:
                        services.add(service)
                    if quantity < 1:
                        msg = _("Quantity must be equal to or greater than 1")
                        form.add_error('quantity', msg)


ServiceItemsFormSet = inlineformset_factory(
                    Report, ServiceItem, formset=ServiceItemsFormset,
                    form=ServiceItemForm, extra=1
                    )


class AdditionalImageForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = AdditionalImage
        fields = ['image']

    def __init__(self, *args, **kwargs):
        super(AdditionalImageForm, self).__init__(*args, **kwargs)
        self.fields['image'].label = _("Images")

    def save(self, *args, **kwargs):
        file_list = self.files.getlist('image')
        position = 1
        if len(file_list)>0:
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
                    if float(price) < 0:
                        msg = _('The Price can\'t be less than 0')
                        form.add_error('price', msg)
                elif form.cleaned_data.get('price') == 0:
                    msg = _('The Price can\'t be 0')
                    form.add_error('price', msg)
            except ValueError:
                msg = _('The Price should be numeric type')
                form.add_error('price', msg)


class ReportTemplateInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        if kwargs['instance'].pk:
            kwargs['initial'] = [
            {'country': country.id } for country in Country.objects.all()
        ]
        super(ReportTemplateInlineFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            country_field = form.fields['country']
            country_field.widget.attrs = {'readonly':'readonly'}
            country_field.widget.can_add_related = False
            country_field.widget.can_change_related = False
            country_field.disabled =  True
