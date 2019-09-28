from django.contrib import admin
from django.urls import path
from django.urls import include

from .views import (
                ReportsListView,
                ReportDetailView,
                ReportCreateView,
                ReportUpdateView,
                ReportDeleteView,
                PriceTableView
                )


urlpatterns = [
        path('', ReportsListView.as_view(), name='reports_list_url'),
        path('create/', ReportCreateView.as_view(), name='report_create_url'),
        path('<int:pk>/update/', ReportUpdateView.as_view(), name='report_update_url'),
        path('<int:pk>/view/', ReportDetailView.as_view(), name='report_detail_url'),
        path('price_table/<int:pk>', PriceTableView.as_view(), name='price_table_url'),
        path('<int:pk>/delete/', ReportDeleteView.as_view(), name='report_delete_url'),
         ]
