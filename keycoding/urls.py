from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home_view, dashboard_view, language_dashboard_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    # Auth ancillary routes (password reset, change) namespaced to avoid collisions
    path('accounts/', include(('django.contrib.auth.urls', 'auth'), namespace='auth')),
    path('contact/', include('contact.urls')),
    # Landing / Sales page (redirects to dashboard if authenticated)
    path('', home_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/<slug:lang>/', language_dashboard_view, name='language_dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
