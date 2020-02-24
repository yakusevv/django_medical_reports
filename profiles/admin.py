from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.urls import resolve

from .models import Profile, ProfileDistrict, ProfileDistrictVisitPrice
from .forms import ProfileDistrictVisitPriceInlineFormSet, ProfileDistrictForm
from reports.models import TypeOfVisit


admin.site.unregister(User)


class EditLinkToInlineObject(object):
    def edit_link(self, instance):
        url = reverse('admin:{}_{}_change'.format(
            instance._meta.app_label,  instance._meta.model_name),  args=[instance.pk] )
        if instance.pk:
            return mark_safe(u'<a href="{u}">edit</a>'.format(u=url))
        else:
            return ''


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fk_name = 'user'


class ProfileDistrictInline(EditLinkToInlineObject, admin.TabularInline):
    model = ProfileDistrict
    readonly_fields = ('edit_link', )
    can_delete = True
    fk_name = 'user'

    def get_parent_object_from_request(self, request):
        resolved = resolve(request.path_info)
        if resolved.kwargs:
            return self.parent_model.objects.get(pk=resolved.kwargs['object_id'])
        return None

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        field = super(ProfileDistrictInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == 'district':
            if request._obj_ is not None:
                field.queryset = field.queryset.filter(
                    region__country = request._obj_.profile.city.district.region.country
                    )
            else:
                field.queryset = field.queryset.none()

        return field


class ProfileDistrictVisitPriceInline(admin.TabularInline):
    model = ProfileDistrictVisitPrice
    formset = ProfileDistrictVisitPriceInlineFormSet
    can_delete = False
    fk_name = 'profile_district'


    def get_parent_object_from_request(self, request):
        resolved = resolve(request.path_info)
        if resolved.kwargs:
            return self.parent_model.objects.get(pk=resolved.kwargs['object_id'])
        return None


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


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, ProfileDistrictInline)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super(CustomUserAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        print(dir(obj))
        covered_districts = obj.profiledistrict_set
        if covered_districts:
            for dist in covered_districts.all():
                if not dist.district.region.country == obj.profile.city.district.region.country:
                    dist.delete()
        super(CustomUserAdmin, self).save_model(request, obj, form, change)


@admin.register(ProfileDistrict)
class ProfileDistrictAdmin(admin.ModelAdmin):
    form = ProfileDistrictForm
    inlines = (ProfileDistrictVisitPriceInline, )
