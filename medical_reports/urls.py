from django.contrib import admin
from django.urls import path
from django.urls import include

from .views import index

urlpatterns = [
    path('', redirect_news, name='redirect_news_url')
    path('admin/', admin.site.urls),
    path('reports/', include('reports.urls')),
]
