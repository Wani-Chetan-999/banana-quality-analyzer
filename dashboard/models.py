from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('operator', 'System Operator'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='operator')

class GradingConfig(models.Model):
    """Dynamically alters the bounds defining banana physical grades."""
    grade_a_min = models.FloatField(default=130.0, help_text="Min weight for Grade A (g)")
    grade_b_min = models.FloatField(default=100.0, help_text="Min weight for Grade B (g)")
    grade_c_min = models.FloatField(default=10.0, help_text="Min weight for Grade C (g)")
    
    class Meta:
        verbose_name = "System Grading Settings"
        verbose_name_plural = "System Grading Settings"

    def determine_grade(self, weight: float) -> str:
        print("Weight:", weight)
        print("A:", self.grade_a_min)
        print("B:", self.grade_b_min)
        print("C:", self.grade_c_min)

        if weight >= self.grade_a_min:
            print("Returning Grade A")
            return "Grade A"
        elif weight >= self.grade_b_min:
            print("Returning Grade B")
            return "Grade B"
        elif weight >= self.grade_c_min:
            print("Returning Grade C")
            return "Grade C"

        print("Returning Reject")
        return "Reject"

class BananaAnalysisReport(models.Model):
    """Stores geometric metadata logs alongside real-world processing assets."""
    top_image_capture = models.ImageField(upload_to='captures/top/')
    side_image_capture = models.ImageField(upload_to='captures/side/')

    # NEW
    top_annotated_image = models.ImageField(
        upload_to="debug/top/",
        blank=True,
        null=True
    )

    side_annotated_image = models.ImageField(
        upload_to="debug/side/",
        blank=True,
        null=True
    )

    calculated_length = models.FloatField()
    calculated_width = models.FloatField()
    calculated_thickness = models.FloatField()
    calculated_area = models.FloatField()
    
    estimated_weight = models.FloatField()
    assigned_grade = models.CharField(max_length=15)
    execution_duration_ms = models.IntegerField()
    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report #{self.id} - {self.assigned_grade} ({self.estimated_weight:.1f}g)"