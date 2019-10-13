from django.contrib import admin
from django.urls import path
from django.urls import include
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.i18n import i18n_patterns

from .views import redirect_news
from . import settings

urlpatterns = [
    path('', redirect_news),
    path('news/', include('blog.urls')),
    path('admin/', admin.site.urls),
    path('reports/', include('reports.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('profiles/', include('profiles.urls'))
]

if settings.DEBUG:
    if settings.MEDIA_ROOT:
        urlpatterns += static(
                            settings.MEDIA_URL,
                            document_root=settings.MEDIA_ROOT
                            )
    urlpatterns += staticfiles_urlpatterns()
