# core_app/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard import views
from dashboard.views import DashboardIndexView, HistoricalAnalysisListView, export_pdf_report_view
from api.views import AnalyzeBananaView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Built-in Auth Handlers (Handles login, logout, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Internal Presentation Application Layers
    path('', DashboardIndexView.as_view(), name='dashboard_home'),
    path('history/', HistoricalAnalysisListView.as_view(), name='historical_logs'),
    path('reports/<int:report_id>/pdf/', export_pdf_report_view, name='generate_pdf_report'),
    
    # Decoupled Core API Systems Route Entries
    path('api/v1/analyze/', AnalyzeBananaView.as_view(), name='api_analyze_banana'),
    path('history/delete/<int:report_id>/',views.delete_report, name='delete_report'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)