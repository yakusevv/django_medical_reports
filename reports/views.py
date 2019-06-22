from django.shortcuts import render
from django.views.generic import ListView, DetailView, DeleteView, View, CreateView
from django.db import transaction

from .models import Report
from .forms import ReportCreateForm, ServiceItemsFormSet

class ReportsListView(ListView):
    model = Report
    template_name = 'reports/reports_list.html'


class ReportDetailView(DetailView):
    model = Report
    template_name = 'reports/report_detail.html'

'''
class ReportCreateView(CreateView):
    template_name = 'reports/report_create.html'

    def get_context_data(self, **kwargs):
        data = super(ReportCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['service_items'] = ServiceItemsFormSet(self.request.POST)
        else:
            data['service_items'] = ServiceItemsFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        service_items = context['service_items']
        with transaction.atomic():
            self.object = form.save()

            if service_items.is_valid():
                service_items.instance = self.object
                service_items.save()
        return super(ReportCreateView, self).form_valid(form)

    def get(self, request):
        form = ReportCreateForm()
        return render(request, self.template_name, context={'form': form})

    def post(self, request):
        bound_form = ReportCreateForm(request.POST)
        if bound_form.is_valid():
            new_report = bound_form.save(commit=False)
            new_report.doctor = request.user.profile
            new_report.save()
            return redirect(new_report)
        return render(request, self.template, context={'form': bound_form})
'''

class ReportCreateView(CreateView):
    template_name = 'reports/report_create.html'
    form_class = ReportCreateForm

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

    def form_valid(self, form):
        context = self.get_context_data()
        service_items = context['service_items']
        with transaction.atomic():
            form.instance.doctor = self.get_form_kwargs()['doctor']
            self.object = form.save()

            if service_items.is_valid():
                service_items.instance = self.object
                service_items.save()
        return super(ReportCreateView, self).form_valid(form)
