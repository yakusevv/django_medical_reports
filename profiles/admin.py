from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.urls import resolve
from django.shortcuts import redirect

from .models import Profile, UserDistrict, UserDistrictVisitPrice
from .forms import UserDistrictVisitPriceInlineFormSet, UserDistrictInlineFormset, UserDistrictForm
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


class UserDistrictInline(EditLinkToInlineObject, admin.TabularInline):
    model = UserDistrict
    readonly_fields = ('edit_link', )
    can_delete = True
    fk_name = 'user'
    formset = UserDistrictInlineFormset

    def get_parent_object_from_request(self, request):
        resolved = resolve(request.path_info)
        if resolved.kwargs:
            return self.parent_model.objects.get(pk=resolved.kwargs['object_id'])
        return None

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):

        field = super(UserDistrictInline, self).formfield_for_manytomany(db_field, request, **kwargs)
#        if db_field.name == 'cities':
#            if request._obj_ is not None:
#                field.queryset = field.queryset.filter(
#                    district__region__country = request._obj_.profile.city.district.region.country
#                    )
#            else:
#                field.queryset = field.queryset.none()

        return field


class UserDistrictVisitPriceInline(admin.TabularInline):
    model = UserDistrictVisitPrice
    formset = UserDistrictVisitPriceInlineFormSet
    can_delete = False
    fk_name = 'user_district'


    def get_parent_object_from_request(self, request):
        resolved = resolve(request.path_info)
        if resolved.kwargs:
            return self.parent_model.objects.get(pk=resolved.kwargs['object_id'])
        return None


    def get_extra(self, request, obj=None, **kwargs):
        parent = self.get_parent_object_from_request(request)
        if parent:
            extra = len(TypeOfVisit.objects.filter(
                country=parent.cities.all()[0].district.region.country
                        ))
            return extra
        return 0

    def get_max_num(self, request, obj=None, **kwargs):
        parent = self.get_parent_object_from_request(request)
        if parent:
            max_num = len(TypeOfVisit.objects.filter(
                country=parent.cities.all()[0].district.region.country
                          ))
            return max_num
        return 0


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, UserDistrictInline)

 #   def get_inline_instances(self, request, obj=None):
 #       if not obj:
 #           return list()
 #       return super(CustomUserAdmin, self).get_inline_instances(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super(CustomUserAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        covered_districts = obj.userdistrict_set
#        if covered_districts:
#            for dist in covered_districts.all():
#                if not dist.district.region.country == obj.profile.city.district.region.country:
#                    dist.delete()
        super(CustomUserAdmin, self).save_model(request, obj, form, change)


@admin.register(UserDistrict)
class UserDistrictAdmin(admin.ModelAdmin):
    form = UserDistrictForm
    inlines = (UserDistrictVisitPriceInline, )

    def response_change(self, request, obj, post_url_continue=None):
        return redirect('/admin/auth/user/{}/change'.format(obj.user.id))
