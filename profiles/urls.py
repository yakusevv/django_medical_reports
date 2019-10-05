from django.contrib import admin
from django.urls import path
from django.urls import include

from .views import (
                ProfileDetailView
                )


urlpatterns = [
        path('<int:pk>/detail', ProfileDetailView.as_view(), name='profile_detail_url'),
         ]
