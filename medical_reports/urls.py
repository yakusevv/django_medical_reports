from django.contrib import admin
from django.urls import path
from django.urls import include

from .views import redirect_news

urlpatterns = [
    path('', redirect_news),
    path('news/', include('blog.urls')),
    path('admin/', admin.site.urls),
    #path('reports/', include('reports.urls')),
]
