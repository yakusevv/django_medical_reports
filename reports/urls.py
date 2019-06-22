from django.contrib import admin
from django.urls import path
from django.urls import include

from .views import ReportsListView, ReportCreateView, ReportDetailView


urlpatterns = [
        path('', ReportsListView.as_view(), name='reports_list_url'),
        path('create/', ReportCreateView.as_view(), name='report_create_url'),
        path('<int:pk>/view/', ReportDetailView.as_view(), name='report_detail_url'),
         ]
