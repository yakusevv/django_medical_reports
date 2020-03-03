from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from django.forms.models import BaseInlineFormSet

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
                        country=kwargs['instance'].district.region.country
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

    def clean(self):
        cleaned_data = super(UserDistrictForm, self).clean()
        user = cleaned_data.get('user')
        district = cleaned_data.get('district')
        if not user.profile.city.district.region.country == district.region.country:
            raise forms.ValidationError("Doctors can't cover districts of foreign country")
        else:
            return cleaned_data
