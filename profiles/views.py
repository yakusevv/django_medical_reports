from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView, CreateView
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.shortcuts import redirect

from .forms import ProfileForm, ProfileReportAutofillTemplateForm
from .models import Profile, ProfileReportAutofillTemplate


class ProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = 'profiles/profile_detail.html'
    model = Profile

    def get(self, request, pk):
        if request.user.profile.pk == pk or request.user.is_staff:
            profile = get_object_or_404(self.model, pk=pk)
            return render(request, self.template_name, context={ 'profile': profile,
                                                                 'profile_link_active': "active"})
        else:
            raise Http404


class ProfileReportAutofillTemplateCreateView(LoginRequiredMixin, CreateView):
    model = ProfileReportAutofillTemplate
    template_name = 'profiles/profile_template_create.html'
    form_class = ProfileReportAutofillTemplateForm

    def get_success_url(self, **kwargs):
        return self.request.user.profile.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super(ProfileReportAutofillTemplateCreateView, self).get_context_data(**kwargs)
        context['profile_link_active'] = "active"
        context['form'].fields['doctor'].initial = self.request.user.profile
        return context


class ProfileReportAutofillTemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = ProfileReportAutofillTemplate
    template_name = 'profiles/profile_template_update.html'
    form_class = ProfileReportAutofillTemplateForm

    def get_success_url(self, **kwargs):
        return self.request.user.profile.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super(ProfileReportAutofillTemplateUpdateView, self).get_context_data(**kwargs)
        context['profile_link_active'] = "active"
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        if self.request.POST.get('Delete'):
            form.instance.delete()
            return redirect(self.get_success_url())
        return super(ProfileReportAutofillTemplateUpdateView, self).form_valid(form)
