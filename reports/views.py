import io
import datetime

from viberbot.api.viber_requests import ViberRequest, ViberMessageRequest
from viberbot.api.messages.text_message import TextMessage

from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.urls import reverse
from django.views.generic import (
                                TemplateView,
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
from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.template.defaultfilters import slugify
from django.conf import settings

from rest_framework import viewsets, permissions
from rest_framework.response import Response

from profiles.models import Profile

from .models import (
                Report,
                Country,
                Region,
                PriceGroup,
                TypeOfVisit,
                VisitTariff,
                City,
                Disease,
                Service,
                Company,
                ReportRequest
                    )

from .forms import (
                ReportForm,
                ServiceItemsFormSet,
                AdditionalImageFormSet,
                DateFilterForm,
                ReportRequestForm,
                )
from .utils import docx_report_generator, reports_xlsx_generator
from .serializers import ReportRequestSerializer, CompanyOptionsSerializer, DoctorOptionsSerializer


@csrf_exempt
def vbr_bot(request):
    if request.method == "GET":
        return HttpResponse(status=404)
    if request.method == "POST":
        viber = settings.VIBER
        if not viber.verify_signature(request.body, request.headers.get('X-Viber-Content-Signature')):
            return Response(status=403)
        viber_request = viber.parse_request(request.body)
        doctors_viber_list = [doctor.viber_id for doctor in Profile.objects.filter(user__is_staff=False)]
        doctors_pk_list = ['#id' + str(doctor.pk) for doctor in Profile.objects.filter(
                                                                    user__is_staff=False,
                                                                    ) if not doctor.viber_id
                           ]
        if isinstance(viber_request, ViberRequest) and viber_request.event_type == 'webhook':
            print("Webhook has been installed successfully")
            return HttpResponse(status=200)
        elif isinstance(viber_request, ViberMessageRequest):
            message = viber_request.message.text
            if not len(doctors_pk_list) and viber_request.sender.id not in doctors_viber_list:
                viber.send_messages(viber_request.sender.id, [
                   TextMessage(text="All users are already authenticated.")
                ])
            elif viber_request.sender.id not in doctors_viber_list:
                viber.send_messages(viber_request.sender.id, [
                   TextMessage(text="Authentication processing...")
                ])
                if message in doctors_pk_list:
                    doctor = Profile.objects.get(pk=message.split('#id')[-1])
                    doctor.viber_id = viber_request.sender.id
                    doctor.save()
                    viber.send_messages(viber_request.sender.id, [
                        TextMessage(text="Success!")
                    ])
                    viber.send_messages(viber_request.sender.id, [
                        TextMessage(text='Welcome, dr. {}!'.format(doctor.user.last_name))
                    ])
                    return HttpResponse(status=200)
                else:
                    viber.send_messages(viber_request.sender.id, [
                        TextMessage(text='Access denied')
                    ])
                    return HttpResponse(status=200)
            else:
                doctor = Profile.objects.get(viber_id=viber_request.sender.id)
                if message.lower() in ('ok', 'ок'):
                    for req in doctor.report_requests.filter(seen=False, status='accepted'):
                        req.seen = True
                        req.save()
                elif message.lower().startswith('#id'):
                    viber.send_messages(viber_request.sender.id, [
                        TextMessage(text='You have been already authenticated as dr. {}'.format(doctor.user.last_name))
                    ])
                else:
                    viber.send_messages(viber_request.sender.id, [
                        TextMessage(text='Wrong command')
                    ])
                return HttpResponse(status=200)
        else:
            return HttpResponse(status=500)
    return HttpResponse(status=200)


@login_required
def download_report_docx(request, pk, type_of_report):
    buffer = io.BytesIO()
    report = Report.objects.get(pk=pk)
    if (request.user.profile == report.report_request.doctor and type_of_report == 'd') or request.user.is_staff:
        file = docx_report_generator(report, type_of_report)
        if file:
            file_name = "_".join((
                            slugify(report.patients_last_name).upper(),
                            slugify(report.patients_first_name).upper(),
                            slugify(report.get_full_company_ref_number).upper()
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
def download_reports_excel(request):
    current_country = request.user.profile.city.district.region.country
    queryset = request.session.get('filtered')
    if queryset:
        reports = Report.objects.filter(pk__in=queryset).order_by('-date_of_visit')
    else:
        reports = Report.objects.filter(
                                    city__district__region__country=current_country
                                    ).order_by('-date_of_visit')
    buffer = io.BytesIO()
    file = reports_xlsx_generator(reports)
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
        user = self.request.user
        return user.is_superuser or user.is_staff


class ReportsListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'reports/reports_list.html'
    ordering = ('checked', '-date_of_visit')
    paginate_by = 30

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
            queries_without_page = self.request.GET.copy()
            if queries_without_page.get('page', ''):
                del queries_without_page['page']
            context['queries'] = queries_without_page
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
                    Q(report_request__ref_number__icontains=search_query) |
                    Q(report_request__company_ref_number__icontains=search_query) |
                    Q(patients_first_name__icontains=search_query) |
                    Q(patients_last_name__icontains=search_query) |
                    Q(patients_date_of_birth__icontains=search_query) |
                    Q(patients_policy_number__icontains=search_query) |
                    Q(city__name__icontains=search_query) |
                    Q(detailed_location__icontains=search_query) |
                    Q(cause_of_visit__icontains=search_query) |
                    Q(checkup__icontains=search_query) |
                    Q(additional_checkup__icontains=search_query) |
                    Q(prescription__icontains=search_query)
                    )
            company_filter = self.request.GET.getlist('company_filter', None)
            if company_filter:
                queryset = queryset.filter(report_request__company__in=company_filter)
            doctor_filter = self.request.GET.getlist('doctor_filter', None)
            if doctor_filter:
                queryset = queryset.filter(report_request__doctor__in=doctor_filter)
            date_field_from = self.request.GET.get('date_field_from', '')
            if date_field_from:
                date_field_from = datetime.datetime.strptime(date_field_from, "%d.%m.%Y").date()
                queryset = queryset.filter(report_request__date_time__gte=date_field_from)
            date_field_to = self.request.GET.get('date_field_to', '')
            if date_field_to:
                date_field_to = datetime.datetime.strptime(date_field_to, "%d.%m.%Y").date()
                queryset = queryset.filter(
                                    report_request__date_time__lt=date_field_to + datetime.timedelta(days=1)
                                    )
        if not self.request.user.is_staff:
            queryset = queryset.filter(report_request__doctor__pk=self.request.user.profile.pk)
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

        if request.user.profile == self.object.report_request.doctor or request.user.is_staff and country_case:
            return self.render_to_response(self.get_context_data())
        else:
            return HttpResponseForbidden('403 Forbidden', content_type='text/html')

    def get_context_data(self, **kwargs):
        context = super(ReportDetailView, self).get_context_data(**kwargs)
        context['report_link_active'] = "active"
        country = self.object.city.district.region.country
        reports_queryset = Report.objects.filter(
            city__district__region__country=country,
            company_ref_number=self.object.company_ref_number
        ).order_by('date_of_visit')
        if len(reports_queryset) > 1:
            context['same_case_reports'] = reports_queryset
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        object_country = self.object.city.district.region.country
        users_country = request.user.profile.city.district.region.country
        country_case = object_country == users_country

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

        if request.POST.get('visit_failed') == "True":
            if request.POST.get('report_request_failed'):
                report_request = get_object_or_404(ReportRequest, pk=request.POST.get('report_request_failed'))
                if report_request.doctor == request.user.profile or request.user.is_staff:
                    report_request.status = 'failed'
                    report_request.save()
                return redirect(reverse('report_create_url'))
            else:
                raise Http404()

        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        service_items = self.get_context_data()['service_items']
        images = self.get_context_data()['images']
        prev = self.request.POST.get('previous_report', None)
        if form.is_valid() and service_items.is_valid() and images.is_valid():
            return self.form_valid(form, service_items, images, prev)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(ReportCreateView, self).get_context_data(**kwargs)
        context['report_link_active'] = "active"
        profile = self.request.user.profile
        profile_country = profile.city.district.region.country
        templates_query = profile.report_templates.filter(country=profile_country)
        report_requests_query = ReportRequest.objects.filter(
                                            doctor__city__district__region__country=profile_country,
                                            report=None,
                                            status='accepted'
                                            ).order_by('-date_time')
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
                template['diagnosis_template'] = [d.pk for d in diagnosis]
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

            context['form'].fields['type_of_visit'].queryset = type_of_visit_set
            context['form'].fields['city'].queryset = city_set
            context['form'].fields['diagnosis'].queryset = disease_set
            if self.request.user.is_staff:
                report_requests = report_requests_query
            else:
                report_requests = report_requests_query.filter(doctor=profile)
            context['form'].fields['report_request'].queryset = report_requests
            context['json_report_requests'] = serialize('json', report_requests, cls=DjangoJSONEncoder)
            for form in context['service_items'].forms:
                form.fields['service'].queryset = service_set
        if self.request.GET.get('prev'):
            report_pk = self.request.GET.get('prev')
            try:
                prev_report = Report.objects.get(pk=report_pk)
            except Report.DoesNotExist:
                prev_report = None
            user = self.request.user
            if prev_report and (prev_report.report_request.doctor == user.profile or user.is_staff):
                context['form'].fields['company_ref_number'].initial     = prev_report.company_ref_number
                context['form'].fields['patients_first_name'].initial    = prev_report.patients_first_name
                context['form'].fields['patients_last_name'].initial     = prev_report.patients_last_name
                context['form'].fields['patients_date_of_birth'].initial = prev_report.patients_date_of_birth
                context['form'].fields['patients_policy_number'].initial = prev_report.patients_policy_number
                context['form'].fields['city'].initial                   = prev_report.city
                context['form'].fields['detailed_location'].initial      = prev_report.detailed_location
                context['form'].fields['cause_of_visit'].initial         = prev_report.cause_of_visit
                context['form'].fields['checkup'].initial                = prev_report.checkup
                context['form'].fields['additional_checkup'].initial     = prev_report.additional_checkup
                context['form'].fields['prescription'].initial           = prev_report.prescription
                context['previous_report']                               = prev_report
        return context

    def form_valid(self, form, service_items, images, prev):
        with transaction.atomic():
            self.object = form.save()
            if service_items.is_valid():
                service_items.instance = self.object
                service_items.save()
            if images.is_valid():
                if prev:
                    prev_report = Report.objects.get(pk=prev)
                    for image in prev_report.additional_images.all():
                        image.pk = None
                        image.report = self.object
                        image.save()
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

        object_country = self.object.city.district.region.country
        users_country = request.user.profile.city.district.region.country
        country_case = object_country == users_country

        if country_case and (request.user.profile == self.object.report_request.doctor or request.user.is_staff):
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

        if country_case and (request.user.profile == self.object.report_request.doctor or request.user.is_staff):
            if not self.object.checked:
                form_class = self.get_form_class()
                form = self.get_form(form_class)
                service_items = self.get_context_data()['service_items']
                if form.is_valid() and service_items.is_valid():
                    return self.form_valid(form, service_items)
                else:
                    return self.form_invalid(form)
            else:
                raise Http404(_("Checked report cannot be edited"))
        else:
            return HttpResponseForbidden('403 Forbidden', content_type='text/html')

    def get_context_data(self, **kwargs):
        context = super(ReportUpdateView, self).get_context_data(**kwargs)
        context['report_link_active'] = "active"
        profile = self.request.user.profile
        profile_country = profile.city.district.region.country
        report_requests_query = ReportRequest.objects.filter(
                                            doctor__city__district__region__country=profile_country
                                            ).filter(
                                            Q(report=None, status='accepted') | Q(report=self.object)
                                            ).order_by('-date_time')
        if self.request.POST:
            context['service_items'] = ServiceItemsFormSet(self.request.POST, instance=self.object)
        else:
            context['service_items'] = ServiceItemsFormSet(instance=self.object)
        if self.request.user.profile.city:
            current_country   = self.request.user.profile.city.district.region.country.pk
            type_of_visit_set = TypeOfVisit.objects.filter(country__pk=current_country)
            city_set          = City.objects.filter(district__region__country=current_country)
            disease_set       = Disease.objects.filter(country=current_country)
            service_set       = Service.objects.filter(country=current_country)

            context['form'].fields['type_of_visit'].queryset = type_of_visit_set
            context['form'].fields['city'].queryset = city_set
            context['form'].fields['diagnosis'].queryset = disease_set
            for form in context['service_items'].forms:
                form.fields['service'].queryset = service_set
            if self.request.user.is_staff:
                report_requests = report_requests_query
            else:
                report_requests = report_requests_query.filter(doctor=profile)
            context['form'].fields['report_request'].queryset = report_requests
            context['json_report_requests'] = serialize('json', report_requests, cls=DjangoJSONEncoder)
        return context

    def form_valid(self, form, service_items):
        with transaction.atomic():
            self.object = form.save()
            if service_items.is_valid():
                service_items.instance = self.object
                service_items.save()
        return super(ReportUpdateView, self).form_valid(form)


class ReportDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'reports/report_delete.html'
    redirect_url = 'reports_list_url'
    model = Report

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        object_country = self.object.city.district.region.country
        users_country = request.user.profile.city.district.region.country
        country_case = object_country == users_country

        if country_case and (request.user.profile == self.object.report_request.doctor or request.user.is_staff):
            if not self.object.checked:
                return render(request, self.template_name, context={
                                                    'report': self.object,
                                                    'report_link_active': "active"
                                                    })
            else:
                raise Http404(_("Checked report cannot be deleted"))
        else:
            return HttpResponseForbidden('403 Forbidden', content_type='text/html')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        object_country = self.object.city.district.region.country
        users_country = request.user.profile.city.district.region.country
        country_case = object_country == users_country

        if country_case and (request.user.profile == self.object.report_request.doctor or request.user.is_staff):
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

        if country_case and (request.user.profile == self.object.report_request.doctor or request.user.is_staff):
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

        if country_case and (request.user.profile == self.object.report_request.doctor or request.user.is_staff):
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
        context = super(PriceTableView, self).get_context_data(**kwargs)
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
                for type_of_visit in types_of_visit:
                    rows[region][district][type_of_visit] = []
                    for group in price_groups:
                        try:
                            rows[region][district][type_of_visit].append(
                                VisitTariff.objects.get(
                                    tariff__district=district,
                                    tariff__price_group=group,
                                    type_of_visit=type_of_visit
                                    ).price)
                        except VisitTariff.DoesNotExist:
                            rows[region][district][type_of_visit].append('')
        context['rows'] = rows
        return context


class ReportRequestViewSet(viewsets.ModelViewSet):
    queryset = ReportRequest.objects.filter(
                                            report=None,
                                            status='accepted'
                                            ).order_by('-date_time')
    serializer_class = ReportRequestSerializer
    permission_classes = (permissions.IsAdminUser,)

    @staticmethod
    def ref_number_changing(prev):
        wrong_data_request = prev
        wrong_data_request.pk = None
        wrong_data_request.status = 'wrong_data'
        wrong_data_request.save()

    @staticmethod
    def get_largest(serializer, instance=False):
        if instance:
            year = instance.date_time.year
        else:
            year = serializer.validated_data['date_time'].year
        company = serializer.validated_data['company']
        country = serializer.validated_data['doctor'].city.district.region.country
        largest = ReportRequest.objects.filter(doctor__city__district__region__country=country,
                                               company=company,
                                               date_time__year=year
                                               )
        if not largest:
            largest = 1
        else:
            largest = largest.order_by('ref_number').last().ref_number + 1
        return largest

    def perform_create(self, serializer):
        serializer.validated_data['date_time'] = datetime.datetime.now()
        serializer.validated_data['sender'] = self.request.user.profile
        if not serializer.validated_data.get('ref_number'):
            serializer.validated_data['ref_number'] = self.get_largest(serializer)
        serializer.save()

    def perform_update(self, serializer):
        if self.request.method == 'PUT':
            instance = self.get_object()
            if instance.company != serializer.validated_data['company']:
                serializer.validated_data['ref_number'] = self.get_largest(serializer, instance=instance)
                serializer.save()
                self.ref_number_changing(instance)
            else:
                serializer.save()
        else:
            serializer.save()


class RequestOptionsViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAdminUser,)

    def list(self, request):
        qs_companies = Company.objects.all()
        country = request.user.profile.city.district.region.country
        context = {'user': self.request.user}
        s1 = CompanyOptionsSerializer(qs_companies, many=True, context=context)
        qs_doctors = Profile.objects.filter(user__is_staff=False, city__district__region__country=country)
        s2 = DoctorOptionsSerializer(qs_doctors, many=True)
        return Response({'companies': s1.data, 'doctors': s2.data})


class ReportRequestsView(AdminStaffRequiredMixin, TemplateView):
    template_name = 'reports/report_requests.html'

    def get_context_data(self, **kwargs):
        current_country = self.request.user.profile.city.district.region.country
        context = super(ReportRequestsView, self).get_context_data()
        context['report_requests_link_active'] = "active"
        regions = Region.objects.filter(country=current_country).order_by('name')
        context['info_table'] = {}
        for region in regions:
            context['info_table'][region] = Profile.objects.filter(
                                                                user__is_staff=False,
                                                                city__district__region=region
                                                                    )
        return context


class ReportRequestsListView(AdminStaffRequiredMixin, ListView):
    model = ReportRequest
    template_name = 'reports/report_requests_list.html'
    ordering = ('-date_time',)
    paginate_by = 30

    def get_context_data(self, *args, **kwargs):
        context = super(ReportRequestsListView, self).get_context_data()
        context['report_requests_link_active'] = "active"
        country = self.request.user.profile.city.district.region.country
        context['doctor_filter'] = Profile.objects.filter(
                                        city__district__region__country=country,
                                        user__is_staff=False
                                        )
        context['company_filter'] = Company.objects.all()
        context['date_filter'] = DateFilterForm()
        context['status_filter'] = {status[0]: status[1] for status in ReportRequest._meta.get_field('status').choices}
        context['report_filter'] = {'1': _("Yes"), '2': _("No")}
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
            status_filter = filters.getlist('status_filter', None)
            if status_filter:
                filters_number += 1
                context['status_filter_selected'] = status_filter
            report_filter = filters.getlist('report_filter', None)
            if '' not in report_filter:
                filters_number += 1
                context['report_filter_selected'] = report_filter
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
            queries_without_page = self.request.GET.copy()
            if queries_without_page.get('page', ''):
                del queries_without_page['page']
            context['queries'] = queries_without_page
            context['filters_number'] = filters_number
        return context

    def get_queryset(self):
        queryset = super(ReportRequestsListView, self).get_queryset()
        doctors_country = self.request.user.profile.city.district.region.country
        queryset = queryset.filter(
                                doctor__city__district__region__country=doctors_country
                                )
        filter_query = self.request.GET.get('usefilter', '')
        if filter_query:
            search_query = self.request.GET.get('search_query', '')
            if search_query:
                queryset = queryset.filter(message__icontains=search_query)
            company_filter = self.request.GET.getlist('company_filter', None)
            if company_filter:
                queryset = queryset.filter(company__in=company_filter)
            doctor_filter = self.request.GET.getlist('doctor_filter', None)
            if doctor_filter:
                queryset = queryset.filter(doctor__in=doctor_filter)
            status_filter = self.request.GET.getlist('status_filter', None)
            if status_filter:
                queryset = queryset.filter(status__in=status_filter)
            report_filter = self.request.GET.getlist('report_filter', None)
            if report_filter:
                if '1' in report_filter:
                    queryset = queryset.exclude(report=None)
                elif '2' in report_filter:
                    queryset = queryset.filter(report=None)
            date_field_from = self.request.GET.get('date_field_from', '')
            if date_field_from:
                date_field_from = datetime.datetime.strptime(date_field_from, "%d.%m.%Y").date()
                queryset = queryset.filter(date_time__gte=date_field_from)
            date_field_to = self.request.GET.get('date_field_to', '')
            if date_field_to:
                date_field_to = datetime.datetime.strptime(date_field_to, "%d.%m.%Y").date()
                queryset = queryset.filter(
                                    date_time__lt=date_field_to + datetime.timedelta(days=1)
                                    )
        return queryset


class ReportRequestUpdateView(AdminStaffRequiredMixin, UpdateView):
    model = ReportRequest
    template_name = 'reports/report_request_update.html'
    form_class = ReportRequestForm

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        object_country = self.object.doctor.city.district.region.country
        users_country = request.user.profile.city.district.region.country
        country_case = object_country == users_country

        if country_case:
            return self.render_to_response(self.get_context_data(form=form))
        else:
            return HttpResponseForbidden('403 Forbidden', content_type='text/html')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        object_country = self.object.doctor.city.district.region.country
        users_country = request.user.profile.city.district.region.country
        country_case = object_country == users_country

        if country_case:
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        else:
            return HttpResponseForbidden('403 Forbidden', content_type='text/html')

    def get_context_data(self, **kwargs):
        context = super(ReportRequestUpdateView, self).get_context_data(**kwargs)
        context['report_requests_link_active'] = "active"
        return context

    def get_success_url(self, **kwargs):
        return reverse('report_requests_list_url')

