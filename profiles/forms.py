from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from django.forms.models import BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _

from .models import Profile, ProfileReportAutofillTemplate, UserDistrict
from reports.models import TypeOfVisit


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = []


class ProfileReportAutofillTemplateForm(forms.ModelForm):

    class Meta:
        model = ProfileReportAutofillTemplate
#        fields = '__all__'
#        widgets = {'doctor': forms.HiddenInput(attrs={})}
        exclude = ('doctor',)

    def clean(self):
        cleaned_data = super(ProfileReportAutofillTemplateForm, self).clean()
        return cleaned_data


class UserDistrictVisitPriceInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        if kwargs['instance'].pk:
            current_instances = [inst.type_of_visit.pk for inst in kwargs['instance'].userdistrictvisitprice_set.all()]
            type_of_visit_filtered = TypeOfVisit.objects.filter(
                        country=kwargs['instance'].cities.all()[0].district.region.country
        ).exclude(
                        pk__in=current_instances
                 )
            kwargs['initial'] = [
            {'type_of_visit': type.id, 'price': '-'} for type in type_of_visit_filtered
        ]
        super(UserDistrictVisitPriceInlineFormSet, self).__init__(*args, **kwargs)
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


class UserDistrictForm(forms.ModelForm):
    class Meta:
        model = UserDistrict
        fields = '__all__'
        exclude = ('cities',)
        
"""
    def clean(self):
        cleaned_data = super(UserDistrictForm, self).clean()
        user = cleaned_data.get('user')
        district = cleaned_data.get('district')
        cities = cleaned_data.get('cities')
        for city in cities:
            if not user.profile.city.district.region.country == city.district.region.country:
                raise forms.ValidationError("Doctors can't cover districts of foreign country")
        else:
            return cleaned_data
"""

class UserDistrictInlineFormset(BaseInlineFormSet):

    def clean(self):
        all_cities = []
        repeated_cities = []
        for form in self.forms:
            if form.cleaned_data.get('cities', False) and not form.cleaned_data.get('DELETE'):
                cities = form.cleaned_data.get('cities').all()
                for city in cities:
                    all_cities.append(city)
            elif form.cleaned_data.get('cities', False) and form.instance:
                form.add_error('cities', _('At least one city must be chosen'))
        if all_cities:
            for city in all_cities:
                if all_cities.count(city)>1:
                    repeated_cities.append(city)
            for form in self.forms:
                if form.cleaned_data and form.cleaned_data.get('cities'):
                    repeated_case = set(repeated_cities) & set(form.cleaned_data.get('cities'))
                    if bool(repeated_case):
                        form.add_error('cities', _('{} - can\'t be dublicated'.format(', '.join(str(city) for city in repeated_case))))
