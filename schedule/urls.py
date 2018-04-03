from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls import url

from schedule.settings import STATIC_URL, STATIC_ROOT,MEDIA_URL,MEDIA_ROOT

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('dashboard/', include('apps.core.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^traductor/', include('rosetta.urls'))
)+static(STATIC_URL, document_root=STATIC_ROOT)

urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
