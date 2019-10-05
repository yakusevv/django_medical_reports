from django.contrib import admin
from django.urls import path
from django.urls import include

from .views import (
                ProfileDetailView,
                ProfileReportAutofillTemplateCreateView
                )


urlpatterns = [
        path('<int:pk>/detail/', ProfileDetailView.as_view(), name='profile_detail_url'),
        path(
             'create_template/',
             ProfileReportAutofillTemplateCreateView.as_view(),
             name='profile_template_create_url'
             )
         ]
