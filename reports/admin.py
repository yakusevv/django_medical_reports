from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import (
                Profile,
                Country,
                Region,
                District,
                City,
                Disease,
                PriceGroup,
                Visit,
                Tariff,
                Company,
                Report,
                AdditionalImage,
                Service,
                ServiceItem,
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

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    pass
