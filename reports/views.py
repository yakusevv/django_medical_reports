import json
import io

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
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.utils.translation import ugettext as _
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required

from profiles.models import Profile, UserDistrict, UserDistrictVisitPrice

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
                Service
                    )
from .forms import (
                ReportForm,
                ServiceItemsFormSet,
                AdditionalImageFormSet
                )
from .utils import DocReportGeneratorWithoutSaving


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
        return context

    def get_queryset(self):
        queryset = super(ReportsListView, self).get_queryset()
        doctors_country = self.request.user.profile.city.district.region.country
        if self.request.user.is_staff:
            queryset = queryset.filter(
                                city__district__region__country=doctors_country
                                )
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(ref_number__icontains=search_query)|
                Q(company_ref_number__icontains=search_query)|
                Q(company__name__icontains=search_query)|
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
        if not self.request.user.is_staff:
            queryset = queryset.filter(doctor=self.request.user.profile.pk)
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
        templates_query = self.request.user.profile.report_templates.all()
        templates = templates_query.values(
                                        'name',
                                        'cause_of_visit_template',
                                        'checkup_template' ,
                                        'additional_checkup_template',
                                        'prescription_template'
                                        )
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
        context['price_groups'] = PriceGroup.objects.all().order_by('pk')
        context['types_of_visit'] = TypeOfVisit.objects.filter(country=country)
        context['price_table_link_active'] = "active"
        return context
