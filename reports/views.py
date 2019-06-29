from django.shortcuts import render
from django.views.generic import ListView, DetailView, DeleteView, View, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

from .models import Report
from .forms import ReportCreateForm, ServiceItemsFormSet

class ReportsListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'reports/reports_list.html'


class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = 'reports/report_detail.html'


class ReportCreateView(LoginRequiredMixin, CreateView):
    template_name = 'reports/report_create.html'
    form_class = ReportCreateForm

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        service_items = self.get_context_data()['service_items']
        if form.is_valid() and service_items.is_valid():
            return self.form_valid(form, service_items)
        else:
            return self.form_invalid(form)



    def get_initial(self, *args, **kwargs):
        initial = super(ReportCreateView, self).get_initial(**kwargs)
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(ReportCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['doctor'] = self.request.user.profile
        return kwargs

    def get_context_data(self, **kwargs):
        data = super(ReportCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['service_items'] = ServiceItemsFormSet(self.request.POST)
        else:
            data['service_items'] = ServiceItemsFormSet()
        return data

    def form_valid(self, form, service_items):
        context = self.get_context_data()
        with transaction.atomic():
            form.instance.doctor = self.get_form_kwargs()['doctor']
            self.object = form.save()
            if service_items.is_valid():
                service_items.instance = self.object
                service_items.save()
        return super(ReportCreateView, self).form_valid(form)
