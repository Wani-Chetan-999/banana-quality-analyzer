from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, Http404
from django.conf import settings
from dashboard.models import BananaAnalysisReport
from utils.pdf_generator import BananaReportGenerator
import os

class DashboardIndexView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the most recent 5 records for the audit feed
        context['recent_logs'] = BananaAnalysisReport.objects.order_by('-processed_at')[:5]
        return context

class HistoricalAnalysisListView(LoginRequiredMixin, ListView):
    model = BananaAnalysisReport
    template_name = "dashboard/history.html"
    context_object_name = "reports"
    paginate_by = 20
    ordering = ['-processed_at']

def export_pdf_report_view(request, report_id):
    """Generates on-the-fly binary data streams of inspection documents."""
    filename = f"Inspection_Report_#{report_id}.pdf"
    output_path = os.path.join(settings.MEDIA_ROOT, 'generated_pdfs', filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        BananaReportGenerator.generate_pdf(report_id, output_path)
        if os.path.exists(output_path):
            return FileResponse(open(output_path, 'rb'), content_type='application/pdf', as_attachment=True, filename=filename)
    except BananaAnalysisReport.DoesNotExist:
        raise Http404("Target report reference does not exist in backend database storage.")

from django.shortcuts import get_object_or_404, redirect
from dashboard.models import BananaAnalysisReport

def delete_report(request, report_id):
    if request.method == "POST":
        report = get_object_or_404(
            BananaAnalysisReport,
            id=report_id
        )
        report.delete()

    return redirect('historical_logs')