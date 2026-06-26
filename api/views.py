# api/views.py
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
from dashboard.models import BananaAnalysisReport, GradingConfig
from utils.cv_engine import BananaCVEngine

class AnalyzeBananaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        start_time = time.time()
        
        top_file = request.FILES.get('top_image')
        side_file = request.FILES.get('side_image')
        
        if not top_file or not side_file:
            return Response(
                {"error": "Missing required top_image or side_image payload files."},
                status=status.HTTP_400_BAD_REQUEST
            )

        import uuid

        top_path = default_storage.save(
            f"tmp/{uuid.uuid4()}.jpg",
            top_file
        )

        side_path = default_storage.save(
            f"tmp/{uuid.uuid4()}.jpg",
            side_file
        )
        
        full_top_path = default_storage.path(top_path)
        full_side_path = default_storage.path(side_path)

        try:
            # Execute the mathematical volume fusion calculation logic directly
            cv_engine = BananaCVEngine()
            results = cv_engine.calculate_3d_mass(full_top_path, full_side_path)

            # Assign matching rules grade configuration properties
            config = GradingConfig.objects.first()
            if not config:
                config = GradingConfig.objects.create()
            assigned_grade = config.determine_grade(results["weight_g"])

            processing_duration = int((time.time() - start_time) * 1000)

            # Store the calculations cleanly inside your history tables log
            record = BananaAnalysisReport.objects.create(
                top_image_capture=top_file,
                side_image_capture=side_file,
                calculated_length=results["length_mm"],
                calculated_width=results["width_mm"],
                calculated_thickness=results["thickness_mm"],
                calculated_area=results["area_mm2"],
                estimated_weight=results["weight_g"],
                assigned_grade=assigned_grade,
                execution_duration_ms=processing_duration
            )

            return Response({
                "id": record.id,
                "metrics": {
                    "length_mm": f"{record.calculated_length:.2f}",
                    "width_mm": f"{record.calculated_width:.2f}",
                    "thickness_mm": f"{record.calculated_thickness:.2f}",
                    "projected_area_mm2": f"{record.calculated_area:.2f}",
                },
                "prediction": {
                    "weight_grams": f"{record.estimated_weight:.2f}",
                    "assigned_grade": record.assigned_grade
                },
                "performance": {
                    "latency_ms": processing_duration
                }
            })
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if default_storage.exists(top_path):
                default_storage.delete(top_path)
            if default_storage.exists(side_path):
                default_storage.delete(side_path)
 