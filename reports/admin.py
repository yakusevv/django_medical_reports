from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Company, Profile, Service, Disease, ServiceItem, Report

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


@admin.register(Report)
class ServiceAdmin(admin.ModelAdmin):
    pass
