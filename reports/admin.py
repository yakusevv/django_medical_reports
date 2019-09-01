from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.forms.models import BaseInlineFormSet
from django import forms
from django.urls import resolve

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
                )


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


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    pass


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    pass


@admin.register(ServiceItem)
class ServiceAdmin(admin.ModelAdmin):
    pass


class AdditionalImageInline(admin.StackedInline):
    model = AdditionalImage
    can_delete = True
    verbose_name_plural = 'ImageField'
    fk_name = 'report'


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    inlines = (AdditionalImageInline, )
    list_filter = (('city__district__region__country', admin.RelatedOnlyFieldListFilter),
                   'city__district__region',
                   'company',
                   'doctor',
                   'checked')

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(ReportAdmin, self).get_inline_instances(request, obj)


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


class VisitTariffInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        kwargs['initial'] = [
            {'type_of_visit': type, 'price': 0} for type in TypeOfVisit.objects.all()
        ]

        super(VisitTariffInlineFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.fields['type_of_visit'].disabled = True


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
        qs = qs.filter(tariff__district=parent.district)
        qs = qs.filter(tariff__price_group=parent.price_group)
        print(qs)
        return qs

    def get_extra(self, request, obj=None, **kwargs):
        parent = self.get_parent_object_from_request(request)
        return len(TypeOfVisit.objects.filter(country=parent.district.region.country))

    def get_max_num(self, request, obj=None, **kwargs):
        parent = self.get_parent_object_from_request(request)
        return len(TypeOfVisit.objects.filter(country=parent.district.region.country))


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    inlines = (VisitTariffInline, )


@admin.register(TypeOfVisit)
class VisitAdmin(admin.ModelAdmin):
    pass
