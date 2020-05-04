from django import forms
from django.forms.models import BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import Select2MultipleWidget

from .models import Profile, ProfileReportAutofillTemplate, UserDistrict
from reports.models import TypeOfVisit


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = []


class ProfileReportAutofillTemplateForm(forms.ModelForm):

    class Meta:
        model = ProfileReportAutofillTemplate
        exclude = ('doctor', 'country')
        widgets = {'diagnosis_template': Select2MultipleWidget, }

    def clean(self):
        cleaned_data = super(ProfileReportAutofillTemplateForm, self).clean()
        return cleaned_data


class UserDistrictVisitPriceInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        if kwargs['instance'].pk:
            type_of_visit_filtered = TypeOfVisit.objects.filter(country=kwargs['instance'].country)
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
        exclude = ('cities', 'country', 'user')


class UserDistrictInlineFormset(BaseInlineFormSet):

    def clean(self):
        all_cities = []
        repeated_cities = []
        for form in self.forms:
            country = form.cleaned_data.get('country', False)
            if form.cleaned_data.get('cities', False) and not form.cleaned_data.get('DELETE'):
                cities = form.cleaned_data.get('cities').all()
                for city in cities:
                    if not country == city.district.region.country:
                        form.add_error('cities', _("Cities of the district must belong to the district's country"))
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
