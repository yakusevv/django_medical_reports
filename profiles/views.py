from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView, CreateView
from django.shortcuts import get_object_or_404
from django.urls import reverse

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

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.doctor = request.user.profile
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


    def get_context_data(self, **kwargs):
        context = super(ProfileReportAutofillTemplateCreateView, self).get_context_data(**kwargs)
        context['profile_link_active'] = "active"
        context['form'].fields['doctor'].initial = self.request.user.profile
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        return super(ProfileReportAutofillTemplateCreateView, self).form_valid(form)
