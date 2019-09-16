from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import resolve
from django.shortcuts import redirect
from django.core.exceptions import ValidationError

from .models import (
                Profile,
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
                ReportTemplate
                )
from .forms import VisitTariffInlineFormSet
from .utils import DocReportGenerator

admin.site.unregister(User)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


class ReportTemplateInline(admin.StackedInline):
    model = ReportTemplate
    can_delete = True
    verbose_name_plural = 'Report Template'


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    inlines = (ReportTemplateInline, )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    pass


class ServiceItemInline(admin.StackedInline):
    model = ServiceItem
    can_delete = True
    verbose_name_plural = 'Service Item'
    fk_name = 'report'

class AdditionalImageInline(admin.StackedInline):
    model = AdditionalImage
    can_delete = True
    verbose_name_plural = 'ImageField'
    fk_name = 'report'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    inlines = (AdditionalImageInline, ServiceItemInline)
    readonly_fields = ('get_total_price',)
    list_display = ('__str__', 'date_of_visit', 'get_total_price', 'checked')
    ordering = ('-date_of_visit',)
    list_filter = (('city__district__region__country', admin.RelatedOnlyFieldListFilter),
                   'city__district__region',
                   'company',
                   'doctor',
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
        if not change and obj.visit_price == 0 or obj.visit_price == 0:
            company = obj.company
            city = obj.city
            type_of_visit = obj.type_of_visit

            district = city.district
            price_group = company.price_group
            try:
                tariff = Tariff.objects.get(district=district, price_group=price_group)
                visit_tariff = VisitTariff.objects.get(tariff=tariff, type_of_visit=type_of_visit)
                obj.visit_price = visit_tariff.price
            except Tariff.DoesNotExist:
                obj.visit_price = 0
        super(ReportAdmin, self).save_model(request, obj, form, change)
        DocReportGenerator(obj)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    pass


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    pass


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(PriceGroup)
class PriceGroupAdmin(admin.ModelAdmin):
    pass


class VisitTariffInline(admin.TabularInline):
    model = VisitTariff
    formset = VisitTariffInlineFormSet
    can_delete = False
    verbose_name_plural = 'Visit Price List'

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


@admin.register(TypeOfVisit)
class VisitAdmin(admin.ModelAdmin):
    pass
