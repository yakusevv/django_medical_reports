from django.contrib import admin
from django.urls import path
from django.urls import include

from .views import (
                ProfileDetailView,
                ProfileListView,
                ProfileReportAutofillTemplateCreateView,
                ProfileReportAutofillTemplateUpdateView,
                )


urlpatterns = [
        path('<int:pk>/detail/', ProfileDetailView.as_view(), name='profile_detail_url'),
        path('list/', ProfileListView.as_view(), name='profiles_list_url'),
        path(
             'templates/create_template/',
             ProfileReportAutofillTemplateCreateView.as_view(),
             name='profile_template_create_url'
             ),
        path(
             'templates/<int:pk>/update_template/',
             ProfileReportAutofillTemplateUpdateView.as_view(),
             name='profile_template_update_url'
             )
         ]
