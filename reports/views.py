import json
import io
import datetime

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.db.models import Q
from django.urls import reverse
from django.views.generic import (
                                View,
                                ListView,
                                DetailView,
                                CreateView,
                                UpdateView,
                                DeleteView
                                )
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpRequest
from django.utils.translation import ugettext as _
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django import forms

from profiles.models import Profile, UserDistrict, UserDistrictVisitPrice
from tempus_dominus.widgets import DatePicker

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
                Company
                    )
from .forms import (
                ReportForm,
                ServiceItemsFormSet,
                AdditionalImageFormSet,
                DateFilterForm
                )
from .utils import DocReportGeneratorWithoutSaving, ReportsXlsxGenerator


@login_required
def downloadReportDocx(request, pk, type):
    buffer = io.BytesIO()
    report = Report.objects.get(pk=pk)
    if (request.user.profile == report.doctor and type == 'd') or request.user.is_staff:
        file = DocReportGeneratorWithoutSaving(report, type)
        if file:
            file_name = "_".join((
                            report.patients_last_name,
                            report.patients_first_name,
                            report.company_ref_number
                            )) + '.docx'
            file.save(buffer)
            buffer.seek(0)
            response = HttpResponse(buffer.read())
            response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)

            return response
        return HttpResponse('<h1>{}</h1>'.format(_('Report template is not found')))
    else:
        return HttpResponseForbidden('403 Forbidden', content_type='text/html')


@login_required
@staff_member_required
@permission_required('reports.can_download_excel')
def downloadReportsExcel(request):
    current_country = request.user.profile.city.district.region.country
    queryset = request.session.get('filtered')
    if queryset:
        reports = Report.objects.filter(pk__in=queryset).order_by('-date_of_visit')
    else:
        reports = Report.objects.filter(
                                    city__district__region__country=current_country
                                    ).order_by('-date_of_visit')
    buffer = io.BytesIO()
    file = ReportsXlsxGenerator(reports)
    if file:
        file_name = datetime.datetime.now().strftime('%d-%m-%Y') + '.xlsx'
        file.save(buffer)
        buffer.seek(0)
        response = HttpResponse(buffer.read())
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
        return response


class AdminStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff


class ReportsListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'reports/reports_list.html'
    ordering = ('checked', '-date_of_visit')
    paginate_by = 20

    def get_context_data(self, *args, **kwargs):
        context = super(ReportsListView, self).get_context_data()
        context['report_link_active'] = "active"
        country = self.request.user.profile.city.district.region.country
        if self.request.user.is_staff:
            context['doctor_filter'] = Profile.objects.filter(
                                        city__district__region__country=country,
                                        user__is_staff=False
                                        )
        context['company_filter'] = Company.objects.all()
        context['date_filter'] = DateFilterForm()
        filters = self.request.GET
        date_filter_initial = {}
        if filters.get('usefilter', ''):
            filters_number = 0
            doctor_filter = filters.getlist('doctor_filter', None)
            if doctor_filter:
                filters_number += 1
                context['doctor_filter_selected'] = doctor_filter
            company_filter = filters.getlist('company_filter', None)
            if company_filter:
                filters_number += 1
                context['company_filter_selected'] = company_filter
            if filters.get('search_query', ''):
                filters_number += 1
                context['search_query_on'] = filters['search_query']
            if filters.get('date_field_from', ''):
                filters_number += 1
                date_filter_initial['date_field_from'] = filters['date_field_from']
            if filters.get('date_field_to', ''):
                filters_number += 1
                date_filter_initial['date_field_to'] = filters['date_field_to']
            if len(date_filter_initial):
                context['date_filter'] = DateFilterForm(initial=date_filter_initial)
            context['filters_number'] = filters_number
        return context

    def get_queryset(self):
        queryset = super(ReportsListView, self).get_queryset()
        doctors_country = self.request.user.profile.city.district.region.country
        if self.request.user.is_staff:
            queryset = queryset.filter(
                                city__district__region__country=doctors_country
                                )
        filter_query = self.request.GET.get('usefilter', '')
        if filter_query:
            search_query = self.request.GET.get('search_query', '')
            if search_query:
                queryset = queryset.filter(
                    Q(ref_number__icontains=search_query)|
                    Q(company_ref_number__icontains=search_query)|
                    Q(patients_first_name__icontains=search_query)|
                    Q(patients_last_name__icontains=search_query)|
                    Q(patients_date_of_birth__icontains=search_query)|
                    Q(patients_policy_number__icontains=search_query)|
                    Q(city__name__icontains=search_query)|
                    Q(detailed_location__icontains=search_query)|
                    Q(cause_of_visit__icontains=search_query)|
                    Q(checkup__icontains=search_query)|
                    Q(additional_checkup__icontains=search_query)|
                    Q(prescription__icontains=search_query)
                    )
            company_filter = self.request.GET.getlist('company_filter', None)
            if company_filter:
                queryset = queryset.filter(company__in=company_filter)
            doctor_filter = self.request.GET.getlist('doctor_filter', None)
            if doctor_filter:
                queryset = queryset.filter(doctor__in=doctor_filter)
            date_field_from = self.request.GET.get('date_field_from', '')
            if date_field_from:
                date_field_from = datetime.datetime.strptime(date_field_from, "%d.%m.%Y").date()
                queryset = queryset.filter(date_of_visit__gte=date_field_from)
            date_field_to = self.request.GET.get('date_field_to', '')
            if date_field_to:
                date_field_to = datetime.datetime.strptime(date_field_to, "%d.%m.%Y").date()
                queryset = queryset.filter(
                                    date_of_visit__lt=date_field_to + datetime.timedelta(days=1)
                                    )
        if not self.request.user.is_staff:
            queryset = queryset.filter(doctor=self.request.user.profile.pk)
        self.request.session['filtered'] = [report.pk for report in queryset]
        return queryset


class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = 'reports/report_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        object_country = self.object.city.district.region.country
        users_country = request.user.profile.city.district.region.country
        country_case = object_country == users_country

        if request.user.profile == self.object.doctor or request.user.is_staff and country_case:
            return self.render_to_response(self.get_context_data())
        else:
            return HttpResponseForbidden('403 Forbidden', content_type='text/html')

    def get_context_data(self, **kwargs):
        context = super(ReportDetailView, self).get_context_data(**kwargs)
        context['report_link_active'] = "active"
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        object_country = self.object.city.district.region.country
        users_country = request.user.profile.city.district.region.country
        country_case = object_country = object_country == users_country

        if request.user.is_staff and request.POST.get('is_checked') and country_case:
            report = self.get_object()
            report.checked = not report.checked
            report.save()
            return redirect(report.get_absolute_url())


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
            print(form.errors)
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(ReportCreateView, self).get_context_data(**kwargs)
        context['report_link_active'] = "active"
        profile_country = self.request.user.profile.city.district.region.country
        templates_query = self.request.user.profile.report_templates.filter(country=profile_country)
        templates = templates_query.values()
        for template in templates:
            template['diagnosis_template'] = Disease.objects.filter(
                                            autofill_template__id=template['id']
                                            )
        for template in templates:
            diagnosis = template['diagnosis_template']
            if not len(diagnosis):
                template['diagnosis_template'] = 'Null'
            else:
                template['diagnosis_template'] = [diag.pk for diag in diagnosis]
        context['json_templates'] = list(templates)
        if self.request.POST:
            context['service_items'] = ServiceItemsFormSet(self.request.POST)
            context['images'] = AdditionalImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['service_items'] = ServiceItemsFormSet()
            context['images'] = AdditionalImageFormSet()
        if self.request.user.profile.city:
            current_country   = self.request.user.profile.city.district.region.country.pk
            type_of_visit_set = TypeOfVisit.objects.filter(country__pk=current_country)
            city_set          = City.objects.filter(district__region__country=current_country)
            disease_set       = Disease.objects.filter(country=current_country)
            service_set       = Service.objects.filter(country=current_country)
            doctors_set       = Profile.objects.filter(
                                city__district__region__country=current_country,
                                user__is_staff=False
                                    )
            context['form'].fields['type_of_visit'].queryset = type_of_visit_set
            context['form'].fields['city'].queryset = city_set
            context['form'].fields['diagnosis'].queryset = disease_set
            if self.request.user.is_staff:
                context['form'].fields['doctor'].required = True
                context['form'].fields['doctor'].queryset = doctors_set
            else:
                context['form'].fields['doctor'].queryset = doctors_set.filter(
                                        pk=self.request.user.profile.pk
                                    )
            for form in context['service_items'].forms:
                form.fields['service'].queryset = service_set
        return context

    def form_valid(self, form, service_items, images):
        with transaction.atomic():
            if not self.request.user.is_staff:
                form.instance.doctor = self.request.user.profile
            self.object = form.save()
            if service_items.is_valid():
                service_items.instance = self.object
                service_items.save()
            if images.is_valid():
                images.instance = self.object
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

        self.object = self.get_object()
        object_country = self.object.city.district.region.country
        users_country = request.user.profile.city.district.region.country
        country_case = object_country == users_country

#        if request.user.profile == self.object.doctor or request.user.is_staff and country_case:
        if country_case and (request.user.profile == self.object.doctor or request.user.is_staff):
            if not self.object.checked:
                return self.render_to_response(self.get_context_data(form=form))
            else:
                raise Http404(_("Checked report cannot be edited"))
        else:
            return HttpResponseForbidden('403 Forbidden', content_type='text/html')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        object_country = self.object.city.district.region.country
        users_country = request.user.profile.city.district.region.country
        country_case = object_country == users_country

        if request.user.profile == self.object.doctor or request.user.is_staff and country_case:
            if not self.object.checked:
                form_class = self.get_form_class()
                form = self.get_form(form_class)
                service_items = self.get_context_data()['service_items']
#            images = self.get_context_data()['images']
#            del_images = [i for i in request.POST.keys() if 'del_image' in i]
                if form.is_valid() and service_items.is_valid(): # and images.is_valid():
#                return self.form_valid(form, service_items, images, del_images)
                    return self.form_valid(form, service_items)#, images)
                else:
                    return self.form_invalid(form)
            else:
                raise Http404(_("Checked report cannot be edited"))
        else:
            return HttpResponseForbidden('403 Forbidden', content_type='text/html')

    def get_context_data(self, **kwargs):
        context = super(ReportUpdateView, self).get_context_data(**kwargs)
        context['report_link_active'] = "active"
        if self.request.POST:
            context['service_items'] = ServiceItemsFormSet(self.request.POST, instance=self.object)
#            context['images'] = AdditionalImageForm(self.request.POST, self.request.FILES)
        else:
            context['service_items'] = ServiceItemsFormSet(instance=self.object)
#            context['images'] = AdditionalImageForm()
        if self.request.user.profile.city:
            current_country   = self.request.user.profile.city.district.region.country.pk
            type_of_visit_set = TypeOfVisit.objects.filter(country__pk=current_country)
            city_set          = City.objects.filter(district__region__country=current_country)
            disease_set       = Disease.objects.filter(country=current_country)
            service_set       = Service.objects.filter(country=current_country)
            doctors_set       = Profile.objects.filter(
                                city__district__region__country=current_country,
                                user__is_staff=False
                                    )
            context['form'].fields['type_of_visit'].queryset = type_of_visit_set
            context['form'].fields['city'].queryset = city_set
            context['form'].fields['diagnosis'].queryset = disease_set
            for form in context['service_items'].forms:
                form.fields['service'].queryset = service_set
            if self.request.user.is_staff:
                context['form'].fields['doctor'].required = True
                context['form'].fields['doctor'].queryset = doctors_set
            else:
                context['form'].fields['doctor'].queryset = doctors_set.filter(
                                        pk=self.request.user.profile.pk
                                    )
        return context

    def form_valid(self, form, service_items): #, images, del_images):
        with transaction.atomic():
            if not self.request.user.is_staff:
                form.instance.doctor = self.request.user.profile
            self.object = form.save()
            if service_items.is_valid():
                service_items.instance = self.object
                service_items.save()
        return super(ReportUpdateView, self).form_valid(form)


class ReportDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'reports/report_delete.html'
    redirect_url = 'reports_list_url'
    model = Report

    def get(self, request, pk):
#        obj = self.model.objects.get(pk=pk)
        self.object = self.get_object()
        object_country = self.object.city.district.region.country
        users_country = request.user.profile.city.district.region.country
        country_case = object_country == users_country

#        if request.user.profile == self.object.doctor or request.user.is_staff and country_case:
        if country_case and (request.user.profile == self.object.doctor or request.user.is_staff):
            if not self.object.checked:
                return render(request, self.template_name, context={
                                                    'report': self.object,
                                                    'report_link_active': "active"
                                                    })
            else:
                raise Http404(_("Checked report cannot be deleted"))
        else:
            return HttpResponseForbidden('403 Frobidden', content_type='text/html')

    def post(self, request, pk):
#        obj = self.model.objects.get(pk=pk)
        self.object = self.get_object()
        object_country = self.object.city.district.region.country
        users_country = request.user.profile.city.district.region.country
        country_case = object_country == users_country

#        if request.user.profile == self.object.doctor or request.user.is_staff and country_case:
        if country_case and (request.user.profile == self.object.doctor or request.user.is_staff):
            if not self.object.checked:
                self.object.delete()
                return redirect(reverse(self.redirect_url))
            else:
                raise Http404(_("Checked report cannot be deleted"))
        else:
            return HttpResponseForbidden('403 Forbidden', content_type='text/html')


class ReportAdditionalImagesUpdateView(LoginRequiredMixin, UpdateView):
    model = Report
    template_name = 'reports/report_images_update.html'
    form_class = AdditionalImageFormSet

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        object_country = self.object.city.district.region.country
        users_country = request.user.profile.city.district.region.country
        country_case = object_country == users_country

#        if request.user.profile == self.object.doctor or request.user.is_staff and country_case:
        if country_case and (request.user.profile == self.object.doctor or request.user.is_staff):
            if not self.object.checked:
                return self.render_to_response(self.get_context_data(form=form))
            else:
                raise Http404(_("Checked report cannot be edited"))
        else:
            return HttpResponseForbidden('403 Forbidden', content_type='text/html')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        object_country = self.object.city.district.region.country
        users_country = request.user.profile.city.district.region.country
        country_case = object_country == users_country

#        if request.user.profile == self.object.doctor or request.user.is_staff and country_case:
        if country_case and (request.user.profile == self.object.doctor or request.user.is_staff):
            if not self.object.checked:
                form_class = self.get_form_class()
                form = self.get_form(form_class)
                if form.is_valid():
                    return self.form_valid(form)
                else:
                    return self.form_invalid(form)
            else:
                raise Http404(_("Checked report cannot be edited"))
        else:
            return HttpResponseForbidden('403 Forbidden', content_type='text/html')

    def get_context_data(self, **kwargs):
        context = super(ReportAdditionalImagesUpdateView, self).get_context_data(**kwargs)
        context['report_link_active'] = "active"
        return context


    def get_success_url(self):
        self.object = self.get_object()
        return reverse("report_update_url", kwargs={"pk": self.object.pk})


class PriceTableView(AdminStaffRequiredMixin, DetailView):
    template_name = 'reports/price_table_view.html'
    model = Country

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        country = kwargs['object']
        price_groups = PriceGroup.objects.all().order_by('pk')
        types_of_visit = TypeOfVisit.objects.filter(country=country)

        context['price_groups'] = price_groups
        context['types_of_visit'] = types_of_visit
        context['price_table_link_active'] = "active"
        rows = {}
        for region in country.region_set.all():
            rows[region] = {}
            for district in region.district_set.all():
                rows[region][district] = {}
                for type in types_of_visit:
                    rows[region][district][type] = []
                    for group in price_groups:
                        try:
                            rows[region][district][type].append(
                            VisitTariff.objects.get(
                                tariff__district=district,
                                tariff__price_group=group,
                                type_of_visit=type
                                ).price)
                        except VisitTariff.DoesNotExist:
                            rows[region][district][type].append('')
        context['rows'] = rows
        return context
