import time
import uuid
import traceback

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

        top_file = request.FILES.get("top_image")
        side_file = request.FILES.get("side_image")

        if not top_file or not side_file:
            return Response(
                {
                    "error": "Both top_image and side_image are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---------------------------------------------------------
        # Save uploaded images temporarily
        # ---------------------------------------------------------

        top_filename = f"{uuid.uuid4()}.jpg"
        side_filename = f"{uuid.uuid4()}.jpg"

        top_path = default_storage.save(
            f"tmp/{top_filename}",
            top_file
        )

        side_path = default_storage.save(
            f"tmp/{side_filename}",
            side_file
        )

        full_top_path = default_storage.path(top_path)
        full_side_path = default_storage.path(side_path)

        try:

            # -----------------------------------------------------
            # CV Processing
            # -----------------------------------------------------

            cv_engine = BananaCVEngine()

            results = cv_engine.calculate_3d_mass(
                full_top_path,
                full_side_path
            )

            # -----------------------------------------------------
            # Determine Grade
            # -----------------------------------------------------

            config = GradingConfig.objects.first()

            if config is None:
                config = GradingConfig.objects.create()

            assigned_grade = config.determine_grade(
                results["weight_g"]
            )

            processing_duration = int(
                (time.time() - start_time) * 1000
            )

            # -----------------------------------------------------
            # Store Report
            # -----------------------------------------------------

            record = BananaAnalysisReport.objects.create(

                calculated_length=results["length_mm"],
                calculated_width=results["width_mm"],
                calculated_thickness=results["thickness_mm"],
                calculated_area=results["area_mm2"],

                estimated_weight=results["weight_g"],
                assigned_grade=assigned_grade,
                execution_duration_ms=processing_duration,
            )

            # Use already-saved files
            record.top_image_capture.name = top_path
            record.side_image_capture.name = side_path

            record.save(
                update_fields=[
                    "top_image_capture",
                    "side_image_capture",
                ]
            )

            # -----------------------------------------------------
            # Response
            # -----------------------------------------------------

            return Response(
             {
                    "id": record.id,

                    "metrics": {
                        "length_mm": round(record.calculated_length, 2),
                        "width_mm": round(record.calculated_width, 2),
                        "thickness_mm": round(record.calculated_thickness, 2),
                        "projected_area_mm2": round(record.calculated_area, 2),
                    },

                    "prediction": {
                        "weight_grams": round(record.estimated_weight, 2),
                        "assigned_grade": record.assigned_grade,
                    },

                    "performance": {
                        "latency_ms": processing_duration
                    },

                    "debug": results["debug"],

                    # NEW
                    "quality": results["quality"]
                }
            )

        except Exception as e:

            traceback.print_exc()

            return Response(
                {
                    "error": str(e),
                    "type": type(e).__name__,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # NOTE:
        # Do NOT delete top_path and side_path.
        # They are now being used by BananaAnalysisReport.