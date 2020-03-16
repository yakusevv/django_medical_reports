from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView, CreateView, ListView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

from .forms import ProfileForm, ProfileReportAutofillTemplateForm
from .models import Profile, ProfileReportAutofillTemplate

from reports.models import TypeOfVisit, Disease
from reports.views import  AdminStaffRequiredMixin


class ProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = 'profiles/profile_detail.html'
    model = Profile

    def get(self, request, pk):
        self.object = self.get_object()
        profile_country = self.object.city.district.region.country
        user_country = request.user.profile.city.district.region.country
        country_case = profile_country == user_country
        if request.user.profile.pk == pk or request.user.is_staff and country_case:
            profile = get_object_or_404(self.model, pk=pk)
            type_of_visit_set = TypeOfVisit.objects.filter(country=profile.city.district.region.country)
            context = {
                      'profile': profile,
                      'type_of_visit_set': type_of_visit_set
                    }
            if profile.pk == request.user.profile.pk:
                context['profile_link_active'] = 'active'
            else:
                context['doctors_list_link_active'] = 'active'
            return render(
                        request,
                        self.template_name,
                        context=context)
        else:
            return HttpResponseForbidden('403 Forbidden', content_type='text/html')


class ProfileListView(AdminStaffRequiredMixin, ListView):
    model = Profile
    template_name = 'profiles/profiles_list.html'
    ordering = ('city__district__region',)

    def get_context_data(self, *args, **kwargs):
        context = super(ProfileListView, self).get_context_data()
        context['doctors_list_link_active'] = "active"
        return context

    def get_queryset(self):
        queryset = super(ProfileListView, self).get_queryset()
        doctors_country = self.request.user.profile.city.district.region.country
        queryset = queryset.filter(
                                city__district__region__country=doctors_country, user__is_staff=False
                                )
        return queryset


class ProfileReportAutofillTemplateCreateView(LoginRequiredMixin, CreateView):
    model = ProfileReportAutofillTemplate
    template_name = 'profiles/profile_template_create.html'
    form_class = ProfileReportAutofillTemplateForm

    def get_success_url(self, **kwargs):
        return self.request.user.profile.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super(ProfileReportAutofillTemplateCreateView, self).get_context_data(**kwargs)
        context['profile_link_active'] = "active"
        context['diagnosis_template'] = Disease.objects.filter(
                                    country=self.request.user.profile.city.district.region.country
                                    )
#        context['form'].fields['doctor'].initial = self.request.user.profile
        return context

    def form_valid(self, form):
        form.instance.doctor = self.request.user.profile
        form.instance.country = self.request.user.profile.city.district.region.country
        self.object = form.save()
        return super(ProfileReportAutofillTemplateCreateView, self).form_valid(form)


class ProfileReportAutofillTemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = ProfileReportAutofillTemplate
    template_name = 'profiles/profile_template_update.html'
    form_class = ProfileReportAutofillTemplateForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        template_country = self.object.doctor.city.district.region.country
        user_country = request.user.profile.city.district.region.country
        country_case = template_country == user_country
        if request.user.profile == self.object.doctor or request.user.is_staff and country_case:
            return self.render_to_response(self.get_context_data())
        else:
            return HttpResponseForbidden('403 Forbidden', content_type='text/html')

    def get_success_url(self, **kwargs):
        return self.object.doctor.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super(ProfileReportAutofillTemplateUpdateView, self).get_context_data(**kwargs)
        if self.object.doctor == self.request.user.profile:
            context['profile_link_active'] = "active"
        else:
            context['doctors_list_link_active'] = "active"
        context['diagnosis_template'] = Disease.objects.filter(
                                            country=self.request.user.profile.city.district.region.country
                                            )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if request.user.profile == self.object.doctor or request.user.is_staff:
            return self.form_valid(form)
        else:
            return HttpResponseForbidden('403 Forbidden', content_type='text/html')

    def form_valid(self, form):
        if self.request.POST.get('Delete'):
            form.instance.delete()
            return redirect(self.get_success_url())
        return super(ProfileReportAutofillTemplateUpdateView, self).form_valid(form)
