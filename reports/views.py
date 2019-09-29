from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
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
from django.http import Http404

from .models import (
                Report,
                Country,
                PriceGroup,
                TypeOfVisit,
                AdditionalImage,
                Tariff,
                VisitTariff,
                City,
                Disease,
                Service,
                Profile
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
    paginate_by = 20


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
        if self.request.user.profile.city:
            current_country   = self.request.user.profile.city.district.region.country.pk
            type_of_visit_set = TypeOfVisit.objects.filter(country__pk=current_country)
            city_set          = City.objects.filter(district__region__country=current_country)
            disease_set       = Disease.objects.filter(country=current_country)
            service_set       = Service.objects.filter(country=current_country)
            data['form'].fields['type_of_visit'].queryset = type_of_visit_set
            data['form'].fields['city'].queryset = city_set
            data['form'].fields['diagnosis'].queryset = disease_set
            for form in data['service_items'].forms:
                form.fields['service'].queryset = service_set
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
        if not self.object.checked:
            return self.render_to_response(self.get_context_data(form=form))
        else:
            raise Http404("Checked report cannot be edited")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.checked:
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            service_items = self.get_context_data()['service_items']
            images = self.get_context_data()['images']
            del_images = [i for i in request.POST.keys() if 'del_image' in i]
            if form.is_valid() and service_items.is_valid() and images.is_valid():
                return self.form_valid(form, service_items, images, del_images)
            else:
                return self.form_invalid(form)
        else:
            raise Http404("Checked report cannot be edited")

    def get_context_data(self, **kwargs):
        data = super(ReportUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['service_items'] = ServiceItemsFormSet(self.request.POST, instance=self.object)
            data['images'] = AdditionalImageForm(self.request.POST, self.request.FILES)
        else:
            data['service_items'] = ServiceItemsFormSet(instance=self.object)
            data['images'] = AdditionalImageForm()
        if self.request.user.profile.city:
            current_country   = self.request.user.profile.city.district.region.country.pk
            type_of_visit_set = TypeOfVisit.objects.filter(country__pk=current_country)
            city_set          = City.objects.filter(district__region__country=current_country)
            disease_set       = Disease.objects.filter(country=current_country)
            service_set       = Service.objects.filter(country=current_country)
            data['form'].fields['type_of_visit'].queryset = type_of_visit_set
            data['form'].fields['city'].queryset = city_set
            data['form'].fields['diagnosis'].queryset = disease_set
            for form in data['service_items'].forms:
                form.fields['service'].queryset = service_set
        return data

    def form_valid(self, form, service_items, images, del_images):
        with transaction.atomic():
            for image in del_images:
                image_pk = image.split('id')[-1:][0]
                AdditionalImage.objects.get(pk=image_pk).delete()
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


class ReportDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'is_staff'
    template_name = 'reports/report_delete.html'
    redirect_url = 'reports_list_url'
    model = Report

    def get(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        if not obj.checked:
            return render(request, self.template_name, context={
                                                'report': obj
                                                })
        else:
            raise Http404("Checked report cannot be deleted")

    def post(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        if not obj.checked:
            obj.delete()
            return redirect(reverse(self.redirect_url))
        else:
            raise Http404("Checked report cannot be deleted")


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


class ProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = 'reports/profile_detail.html'
    model = Profile

    def get(self, request, pk):
        if request.user.profile.pk == pk or request.user.is_staff:
            profile = get_object_or_404(self.model, pk=pk)
            return render(request, self.template_name, context={'profile': profile})
        else:
            raise Http404
