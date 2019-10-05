from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from django.forms.models import BaseInlineFormSet

from .models import Profile, ProfileReportAutofillTemplate


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = []


class ProfileReportAutofillTemplateForm(forms.ModelForm):

    class Meta:
        model = ProfileReportAutofillTemplate
        fields = '__all__'
        widgets = {'doctor': forms.HiddenInput(attrs={})}

    def clean(self):
        cleaned_data = super(ProfileReportAutofillTemplateForm, self).clean()
        return cleaned_data
