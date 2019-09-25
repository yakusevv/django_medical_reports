from django.shortcuts import render
from django.views.generic import (
                                View,
                                ListView,
                                DetailView,
                                CreateView,
                                UpdateView,
                                DeleteView
                                )
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import transaction

from .models import (
                Report,
                Country,
                PriceGroup,
                TypeOfVisit,
                AdditionalImage,
                Tariff,
                VisitTariff
                    )
from .forms import (
                ReportForm,
                ServiceItemsFormSet,
                AdditionalImageForm
                )


class ReportsListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'reports/reports_list.html'
    ordering = ('checked', '-date_of_visit')


class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = 'reports/report_detail.html'


class ReportCreateView(LoginRequiredMixin, CreateView):
    template_name = 'reports/report_create.html'
    form_class = ReportForm

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
        images = self.get_context_data()['images']
        if form.is_valid() and service_items.is_valid() and images.is_valid():
            return self.form_valid(form, service_items, images)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        data = super(ReportCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['service_items'] = ServiceItemsFormSet(self.request.POST)
            data['images'] = AdditionalImageForm(self.request.POST, self.request.FILES)
        else:
            data['service_items'] = ServiceItemsFormSet()
            data['images'] = AdditionalImageForm()
        return data

    def form_valid(self, form, service_items, images):
        context = self.get_context_data()
        with transaction.atomic():
            form.instance.doctor = self.request.user.profile
            company = form.cleaned_data['company']
            city = form.cleaned_data['city']
            type_of_visit = form.cleaned_data['type_of_visit']
            district = city.district
            price_group = company.price_group
            try:
                tariff = Tariff.objects.get(district=district, price_group=price_group)
                visit_tariff = VisitTariff.objects.get(tariff=tariff, type_of_visit=type_of_visit)
                form.instance.visit_price = visit_tariff.price
            except Tariff.DoesNotExist:
                form.instance.visit_price = 0
            self.object = form.save()
            if service_items.is_valid():
                service_items.instance = self.object
                service_items.save()
            if images.is_valid():
                images.instance.report = self.object
                images.save()
        return super(ReportCreateView, self).form_valid(form)


class ReportUpdateView(LoginRequiredMixin, UpdateView):
    model = Report
    template_name = 'reports/report_update.html'
    form_class = ReportForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        service_items = self.get_context_data()['service_items']
        images = self.get_context_data()['images']
        if form.is_valid() and service_items.is_valid() and images.is_valid():
            return self.form_valid(form, service_items, images)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        data = super(ReportUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['service_items'] = ServiceItemsFormSet(self.request.POST, instance=self.object)
            data['images'] = AdditionalImageForm(self.request.POST, self.request.FILES)
        else:
            data['service_items'] = ServiceItemsFormSet(instance=self.object)
            data['images'] = AdditionalImageForm()
        return data

    def form_valid(self, form, service_items, images):
        with transaction.atomic():
            company = form.cleaned_data['company']
            city = form.cleaned_data['city']
            type_of_visit = form.cleaned_data['type_of_visit']
            district = city.district
            price_group = company.price_group
            try:
                tariff = Tariff.objects.get(district=district, price_group=price_group)
                visit_tariff = VisitTariff.objects.get(tariff=tariff, type_of_visit=type_of_visit)
                form.instance.visit_price = visit_tariff.price
            except Tariff.DoesNotExist:
                form.instance.visit_price = 0
            self.object = form.save()
            if service_items.is_valid():
                service_items.instance = self.object
                service_items.save()
            if images.is_valid():
                images.instance.report = self.object
                images.save()
        return super(ReportUpdateView, self).form_valid(form)


class PriceTableView(PermissionRequiredMixin, DetailView):
    permission_required = 'is_staff'
    template_name = 'reports/price_table_view.html'
    model = Country

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        country = kwargs['object']
        context['price_groups'] = PriceGroup.objects.all()
        context['types_of_visit'] = TypeOfVisit.objects.filter(country=country)
        return context
