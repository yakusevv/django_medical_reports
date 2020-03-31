from django.contrib import admin
from django.urls import resolve
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.urls import reverse

from .models import (
                Country,
                Region,
                District,
                City,
                Disease,
                PriceGroup,
                TypeOfVisit,
                Tariff,
                Company,
                Report,
                AdditionalImage,
                Service,
                ServiceItem,
                VisitTariff,
                ReportTemplate,
                ReportRequest
                )
from .forms import VisitTariffInlineFormSet #, ReportTemplateInlineFormSet


class EditLinkToInlineObject(object):

    def edit_link(self, instance):
        url = reverse('admin:{}_{}_change'.format(
            instance._meta.app_label,  instance._meta.model_name),  args=[instance.pk] )
        if instance.pk:
            return mark_safe(u'<a href="{u}">edit</a>'.format(u=url))
        else:
            return ''


class ReportTemplateInline(admin.StackedInline):
    model = ReportTemplate
#    formset = ReportTemplateInlineFormSet
    can_delete = True
'''
    def get_parent_object_from_request(self, request):
        resolved = resolve(request.path_info)
        if resolved.kwargs:
            return self.parent_model.objects.get(pk=resolved.kwargs['object_id'])
        return None

    def get_extra(self, request, obj=None, **kwargs):
        if self.get_parent_object_from_request(request):
            extra = len(Country.objects.all())
            return extra
        return 0

    def get_max_num(self, request, obj=None, **kwargs):
        if self.get_parent_object_from_request(request):
            max_num = len(Country.objects.all())
            return max_num
        return 0
'''


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    pass
#    inlines = (ReportTemplateInline, )

#    def response_add(self, request, obj, post_url_continue=None):
#        return redirect('/admin/reports/company/{}/change'.format(obj.id))


class ServiceInline(admin.StackedInline):
    model = Service
    can_delete = True
    extra = 1


class TypeOfVisitInline(admin.TabularInline):
    model = TypeOfVisit
    can_delete = True
    extra = 1


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    pass


class ServiceItemInline(admin.StackedInline):
    model = ServiceItem
    can_delete = True
    fk_name = 'report'
    extra = 1


class AdditionalImageInline(admin.StackedInline):
    model = AdditionalImage
    can_delete = True
    fk_name = 'report'
    extra = 1


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    inlines = (AdditionalImageInline, ServiceItemInline)
    readonly_fields = ('get_total_price', 'get_total_price_doctor')
    list_display = ('__str__', 'date_of_visit', 'get_total_price', 'get_total_price_doctor', 'checked')
    ordering = ('-date_of_visit',)
    list_filter = (('city__district__region__country', admin.RelatedOnlyFieldListFilter),
                   'city__district__region',
                   'report_request__company',
                   'report_request__doctor',
                   'checked')

    def get_inline_instances(self, request, obj=None):
        return super(ReportAdmin, self).get_inline_instances(request, obj)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, ServiceItem):
                if not instance.pk and instance.service_price == 0:
                    service = instance.service
                    instance.service_price = Service.objects.get(pk=service.pk).price
                    instance.save()
        formset.save_m2m()
        super(ReportAdmin, self).save_formset(request, form, formset, change)

    def save_model(self, request, obj, form, change):
        obj.patients_last_name = obj.patients_last_name.upper()
        obj.patients_first_name = obj.patients_first_name.upper()
#        obj.ref_number = obj.ref_number.upper()
#        obj.company_ref_number = obj.company_ref_number.upper()
#        if not change and obj.visit_price == 0 or obj.visit_price == 0:
#            company = obj.report_request.company
#            city = obj.city
#            type_of_visit = obj.type_of_visit

#            district = city.district
#            price_group = company.price_group
#            try:
#                tariff = Tariff.objects.get(district=district, price_group=price_group)
#                visit_tariff = VisitTariff.objects.get(tariff=tariff, type_of_visit=type_of_visit)
#                obj.visit_price = visit_tariff.price
#                obj.visit_price_doctor = visit_tariff.price_doctor
#                obj.visit_price_doctor = 0 #temporarily
#            except Tariff.DoesNotExist:
#                obj.visit_price = 0
#                obj.visit_price_doctor = 0
        super(ReportAdmin, self).save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        return redirect('/admin/reports/report/{}/change'.format(obj.id))


class CityInline(admin.StackedInline):
    model = City
    can_delete = True


class DistrictInline(EditLinkToInlineObject, admin.StackedInline):
    model = District
    readonly_fields = ('edit_link', )
    can_delete = True
    extra = 1


class RegionInline(EditLinkToInlineObject, admin.StackedInline):
    model = Region
    readonly_fields = ('edit_link', )
    can_delete = True
    extra = 1


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    inlines = ( ReportTemplateInline, RegionInline, TypeOfVisitInline, ServiceInline)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    inlines = (DistrictInline, )


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    inlines = (CityInline, )


@admin.register(PriceGroup)
class PriceGroupAdmin(admin.ModelAdmin):
    pass


class VisitTariffInline(admin.TabularInline):
    model = VisitTariff
    formset = VisitTariffInlineFormSet
    can_delete = False

    def get_parent_object_from_request(self, request):
        resolved = resolve(request.path_info)
        if resolved.kwargs:
            return self.parent_model.objects.get(pk=resolved.kwargs['object_id'])
        return None

    def get_queryset(self, request):
        qs = super(VisitTariffInline, self).get_queryset(request)
        parent = self.get_parent_object_from_request(request)
        if parent:
            qs = qs.filter(tariff__district=parent.district)
            qs = qs.filter(tariff__price_group=parent.price_group)
            return qs
        return qs

    def get_extra(self, request, obj=None, **kwargs):
        parent = self.get_parent_object_from_request(request)
        if parent:
            extra = len(TypeOfVisit.objects.filter(country=parent.district.region.country))
            return extra
        return 0

    def get_max_num(self, request, obj=None, **kwargs):
        parent = self.get_parent_object_from_request(request)
        if parent:
            max_num = len(TypeOfVisit.objects.filter(country=parent.district.region.country))
            return max_num
        return 0


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    inlines = (VisitTariffInline, )

    def response_add(self, request, obj, post_url_continue=None):
        return redirect('/admin/reports/tariff/{}/change'.format(obj.id))


@admin.register(ReportRequest)
class ReportRequest(admin.ModelAdmin):
    list_display = ('__str__', 'status', 'has_report')
    list_filter = ('status', 'company', 'doctor')
    ordering = ('status', '-date_time')

    def has_report(self, obj):
        return obj.has_report()

    has_report.boolean = True
