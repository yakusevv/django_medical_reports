from django.contrib import admin
from django.urls import path, re_path
from django.urls import include
from django.views.generic.base import TemplateView
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from .views import (
                ReportsListView,
                ReportDetailView,
                ReportCreateView,
                ReportUpdateView,
                ReportDeleteView,
                ReportAdditionalImagesUpdateView,
                PriceTableView,
                downloadReportDocx,
                downloadReportsExcel,
                ReportRequestViewSet
                )


router = routers.DefaultRouter()
router.register(r'', ReportRequestViewSet, basename='requests')

urlpatterns = [
        path('', ReportsListView.as_view(), name='reports_list_url'),
        path('create/', ReportCreateView.as_view(), name='report_create_url'),
        path('<int:pk>/update/', ReportUpdateView.as_view(), name='report_update_url'),
        path('<int:pk>/update/images/',
            ReportAdditionalImagesUpdateView.as_view(),
            name='report_images_update_url'
            ),
        path('<int:pk>/view/', ReportDetailView.as_view(), name='report_detail_url'),
        path('price_table/<int:pk>/', PriceTableView.as_view(), name='price_table_url'),
        path('<int:pk>/delete/', ReportDeleteView.as_view(), name='report_delete_url'),
        re_path('(?P<pk>\d+)/view/download/(?P<type>[a,d])/', downloadReportDocx, name='download_report_docx_url'),
        path('download_xlsx/', downloadReportsExcel, name='download_reports_xlsx_url'),
#        path('report_requests/', include((router.urls, 'requests'))),
#        path('report_requests/api-auth/', include('rest_framework.urls', namespace='rest_framework'))
        re_path('report_requests/.*',
                    TemplateView.as_view(template_name='reports/report_requests.html'),
                    name='report_requests_url'
                ),
        path('report_requests-token-auth/', obtain_jwt_token),
        path('report_requests-token-refresh/', refresh_jwt_token)
         ]
