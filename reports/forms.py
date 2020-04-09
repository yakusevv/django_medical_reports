from django import forms
from django.forms.models import inlineformset_factory
from django.forms.models import BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _
from django.core.files.base import ContentFile

from tempus_dominus.widgets import DateTimePicker, DatePicker
from django_select2.forms import Select2MultipleWidget, Select2Widget
from PIL import Image
import io

from .models import (
                    Report,
                    ServiceItem,
                    AdditionalImage,
                    TypeOfVisit,
                    VisitTariff,
                    Tariff,
                    ReportRequest,
                    )
from profiles.models import UserDistrict, UserDistrictVisitPrice


class ReportForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['visit_price'].required = False
        self.fields['visit_price_doctor'].required = False

    class Meta:
        model = Report
        exclude = [
            'checked',
                  ]
        widgets = {
                   'diagnosis'         : Select2MultipleWidget,
                   'city'              : Select2Widget,
                   'type_of_visit'     : Select2Widget,
                   'date_of_visit'     : DateTimePicker(
                                        options={
                                         #   'minDate': '-1y',
                                            'useCurrent': 'hour',
                                            'maxDate': 'now',
                                            'format': "DD.MM.YYYY HH:mm",
                                            'stepping': 5
                                            },
                                        attrs={
                                            'append': 'fa fa-calendar',
                                            'icon_toggle': True,
                                            'size': 'small'
                                            }
                                    ),
                   'patients_date_of_birth': DatePicker(
                                        options={
                                            'useCurrent': False,
                                            'viewMode': 'decades',
                                            'maxDate': 'now'
                                            },
                                        attrs={
                                            'append': 'fa fa-calendar',
                                            'icon_toggle': True,
                                            'size': 'small',
                                            }
                                    ),
                   }

    def clean(self):
        cleaned_data = super(ReportForm, self).clean()
        patients_first_name = cleaned_data.get("patients_first_name").upper()
        patients_last_name = cleaned_data.get("patients_last_name").upper()
        company_ref_number = cleaned_data.get("company_ref_number").upper()
        cleaned_data['patients_last_name'] = patients_last_name
        cleaned_data['patients_first_name'] = patients_first_name
        cleaned_data['company_ref_number'] = company_ref_number
        return cleaned_data

    def save(self, commit=True, *args, **kwargs):
        instance = super(ReportForm, self).save(commit=False)
        report_request = self.cleaned_data['report_request']
        city = self.cleaned_data['city']
        type_of_visit = self.cleaned_data['type_of_visit']
        district = city.district
        price_group = report_request.company.price_group

        decisive_fields = {
                            'report_request',
                            'type_of_visit',
                            'city'
        }
        changed_data_set = set(self.changed_data)
        change_condition = bool(decisive_fields & changed_data_set)

        if instance.report_request.status == 'cancelled_by_company':
            instance.visit_price = 0
        elif not self.cleaned_data.get('visit_price', False) and change_condition:
            try:
                tariff = Tariff.objects.get(district=district, price_group=price_group)
                visit_tariff = VisitTariff.objects.get(tariff=tariff, type_of_visit=type_of_visit)
                instance.visit_price = visit_tariff.price
            except (Tariff.DoesNotExist, VisitTariff.DoesNotExist):
                instance.visit_price = 0
        if not self.cleaned_data.get('visit_price_doctor', False) and change_condition:
            if instance.report_request.doctor.is_owner:
                instance.visit_price_doctor = instance.visit_price
            else:
                try:
                    user_district = UserDistrict.objects.get(cities__in=[city, ], user=report_request.doctor.user)
                    visit_price = UserDistrictVisitPrice.objects.get(
                                                                   user_district=user_district,
                                                                   type_of_visit=type_of_visit
                                                                     )
                    instance.visit_price_doctor = visit_price.price
                except (UserDistrict.DoesNotExist, UserDistrictVisitPrice.DoesNotExist):
                    instance.visit_price_doctor = 0
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class ServiceItemForm(forms.ModelForm):

    class Meta:
        model = ServiceItem
        fields = [
            'service',
            'quantity',
            'cost_doctor',
            'cost'
            ]
        widgets = {
                   'service': Select2Widget,
                   }

    def __init__(self, *args, **kwargs):
        super(ServiceItemForm, self).__init__(*args, **kwargs)
        self.fields['cost'].required = False
        self.fields['cost'].widget.attrs['style'] = 'width: 100px'
        self.fields['cost_doctor'].required = False
        self.fields['cost_doctor'].widget.attrs['style'] = 'width: 100px'
        self.fields['quantity'].widget.attrs['style'] = 'width: 100px'
        self.fields['service'].required = False
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['service'].disabled = True

    def clean(self):
        cleaned_data = super(ServiceItemForm, self).clean()
        if self.instance.id and cleaned_data.get('service', False):
            if cleaned_data['DELETE']:
                self.instance.delete()
        return cleaned_data

    def save(self, commit=True, *args, **kwargs):
        instance = super(ServiceItemForm, self).save(commit=False)
        service = self.cleaned_data.get('service')

        decisive_fields = {
                            'quantity',
                            'service',
                }

        changed_data_set = set(self.changed_data)
        change_condition = bool(decisive_fields & changed_data_set)

        if service:
            cost = self.cleaned_data.get('cost', False)
            cost_doctor = self.cleaned_data.get('cost_doctor', False)
            if instance.report.report_request.status == 'cancelled_by_company':
                instance.cost = 0
            elif not cost and change_condition:
                instance.cost = service.price * instance.quantity
            if not cost_doctor and change_condition:
                if instance.report.report_request.doctor.is_owner:
                    instance.cost_doctor = instance.cost
                elif not service.unsummable_price:
                    instance.cost_doctor = service.price_doctor * instance.quantity
                else:
                    instance.cost_doctor = service.price_doctor
            if commit:
                instance.save()
            return instance


class ServiceItemsFormset(BaseInlineFormSet):

    def clean(self):
        if any(self.errors):
            print(self.errors)
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
    image = forms.ImageField(widget=forms.FileInput(attrs={'onchange': 'addImageCrop(id)'}), required=False, )
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    w = forms.FloatField(widget=forms.HiddenInput())
    h = forms.FloatField(widget=forms.HiddenInput())
    orient = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = AdditionalImage
        fields = ('image', 'expand', 'x', 'y', 'w', 'h', 'orient')

    def clean(self):
        cleaned_data = super(AdditionalImageForm, self).clean()
        if cleaned_data['DELETE'] and self.instance.pk:
            self.instance.delete()
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(AdditionalImageForm, self).__init__(*args, **kwargs)
        self.fields['image'].label = _("Images")
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['image'].disabled = True
        self.fields['x'].required = False
        self.fields['y'].required = False
        self.fields['w'].required = False
        self.fields['h'].required = False
        self.fields['orient'].required = False

    def save(self, commit=True, *args, **kwargs):
        instance = super(AdditionalImageForm, self).save(commit=False)
        image = self.cleaned_data.get('image')
        if image:
            x = self.cleaned_data.get('x')
            y = self.cleaned_data.get('y')
            w = self.cleaned_data.get('w')
            h = self.cleaned_data.get('h')
            orient = self.cleaned_data.get('orient')
            instance.position = 0
            coords = (x, y, w, h)
            if any(coords) and not None in coords:
                rotated_image = Image.open(image)
                if orient == 1:
                    rotated_image = Image.open(image).rotate(0, expand=True)
                elif orient == 6:
                    rotated_image = Image.open(image).rotate(270, expand=True)
                elif orient == 3:
                    rotated_image = Image.open(image).rotate(180, expand=True)
                elif orient == 8:
                    rotated_image = Image.open(image).rotate(90, expand=True)
                cropped_image = rotated_image.crop((x, y, w, h))
                thumb_io = io.BytesIO()
                cropped_image.save(thumb_io, image.content_type.split('/')[-1].upper())
                instance.image.save(str(image).split('/')[-1], ContentFile(thumb_io.getvalue()), save=False)
            if commit:
                instance.save()
            return instance


class AdditionalImageFormset(BaseInlineFormSet):

    def clean(self):
        if any(self.errors):
            print(self.errors)
            return
        number_of_forms = 0
        for form in self.forms:
            if form.cleaned_data:
                if not form.cleaned_data['DELETE']:
                    number_of_forms += 1
                    form.cleaned_data['position'] = number_of_forms


AdditionalImageFormSet = inlineformset_factory(
                    Report, AdditionalImage, formset=AdditionalImageFormset,
                    form=AdditionalImageForm, extra=1
                    )


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
            type_of_visit_field.widget.attrs = {'readonly': 'readonly'}
            type_of_visit_field.widget.can_add_related = False
            type_of_visit_field.widget.can_change_related = False
            type_of_visit_field.disabled = True

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


class DateFilterForm(forms.Form):
    date_field_from = forms.DateField(widget=DatePicker(
                                        options={
                                            'useCurrent': True,
                                            'data-date-end-date': "0d",
                                            'maxDate': 'now'
                                            },
                                        attrs={
                                            'append': 'fa fa-calendar',
                                            'icon_toggle': True,
                                            'size': 'small'
                                            }
                                    ),)
    date_field_to = forms.DateField(widget=DatePicker(
                                        options={
                                            'useCurrent': True,
                                            'maxDate': 'now'
                                            },
                                        attrs={
                                            'append': 'fa fa-calendar',
                                            'icon_toggle': True,
                                            'size': 'small',
                                            }
                                    ),)

    def __init__(self, *args, **kwargs):
        super(DateFilterForm, self).__init__(*args, **kwargs)
        self.fields['date_field_from'].required = False
        self.fields['date_field_to'].required = False


class ReportRequestForm(forms.ModelForm):

    class Meta:
        model = ReportRequest
        fields = ('status', 'date_time',)
        widgets = {
            'date_time': DateTimePicker(
                options={
                    'maxDate': 'now',
                    'format': "DD.MM.YYYY HH:mm",
                    'stepping': 5
                },
                attrs={
                    'append': 'fa fa-calendar',
                    'icon_toggle': True,
                    'size': 'small'
                }
            ),
        }

    def save(self, commit=True, *args, **kwargs):
        instance = super(ReportRequestForm, self).save(commit=False)

        if instance.has_report():
            print('zero')
            instance.report.visit_price = 0
            instance.report.save()
            for item in instance.report.service_items.all():
                item.cost = 0
                item.save()
        if commit:
            instance.save()
        return instance
