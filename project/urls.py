from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from auction.views import show_upcoming
from django.http import HttpResponse


urlpatterns = [
    path('', show_upcoming, name='homepage'),
    path('health/', lambda request: HttpResponse('okay')),
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('auction/', include('auction.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)