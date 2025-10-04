from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('accounts/', include('accounts.urls')),
    
    # Dashboard URL (direct to view)
    path('dashboard/', TemplateView.as_view(template_name='accounts/dashboard.html'), name='dashboard'),
    
    # App URLs
    path('schedules/', include('schedules.urls')),
    path('clients/', include('clients.urls')),
    path('reports/', include('reports.urls')),
    
    # Root redirect to dashboard
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    
    # Demo page
    path('demo/', TemplateView.as_view(template_name='demo.html'), name='demo'),
    # Demo page for shadcn-django components
    path('shadcn-demo/', TemplateView.as_view(template_name='shadcn_demo.html'), name='shadcn_demo'),
    path('basecoat-demo/', TemplateView.as_view(template_name='basecoat_demo.html'), name='basecoat_demo'),
    path('tailwind-demo/', TemplateView.as_view(template_name='tailwind_demo.html'), name='tailwind_demo'),
    path('bootstrap-demo/', TemplateView.as_view(template_name='bootstrap_demo.html'), name='bootstrap_demo'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)