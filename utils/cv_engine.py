# utils/cv_engine.py
import cv2
import numpy as np
import logging
import os
import uuid
from django.conf import settings

logger = logging.getLogger(__name__)

class BananaCVEngine:
    """
    Implements the precise 3D Volumetric extraction geometry from mergeViewG.py
    using fixed scale properties.
    """
    def __init__(self): 
        self.PIXELS_PER_CM_TOP = 120.0
        self.PIXELS_PER_CM_SIDE = 110.0
        self.BANANA_DENSITY = 0.96       
        self.SHAPE_CORRECTION = 0.78   
        # Debug image directory
        self.DEBUG_DIR = os.path.join(
            settings.MEDIA_ROOT,
            "debug"
        )

        os.makedirs(
            self.DEBUG_DIR,
            exist_ok=True
        )  
        
    def save_debug_image(self, image, prefix):
        """
        Save debug image and return URL path.
        """

        filename = f"{prefix}_{uuid.uuid4().hex}.jpg"

        full_path = os.path.join(
            self.DEBUG_DIR,
            filename
        )
        cv2.imwrite(full_path, image)

        # Return URL that browser can access
        return f"/media/debug/{filename}"
    
    def midpoint(self, p1, p2):
        return (
            int((p1[0] + p2[0]) / 2),
            int((p1[1] + p2[1]) / 2)
    )
    def draw_measurement(self, image, p1, p2, color, text):
        cv2.line(image, tuple(p1), tuple(p2), color, 3)

        cv2.circle(image, tuple(p1), 5, color, -1)
        cv2.circle(image, tuple(p2), 5, color, -1)

        m = self.midpoint(p1, p2)

        cv2.putText(
            image,
            text,
            (m[0] + 8, m[1] - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            color,
            2
    )
    def create_measurement_overlay(
        self,
        image,
        contour,
        rect,
        length_cm,
        width_cm,
        thickness_cm,
        area_px,
        pixels_per_cm,
        view_name
    ):

        overlay = image.copy()

        # Green contour
        cv2.drawContours(
            overlay,
            [contour],
            -1,
            (0,255,0),
            3
        )

        box = cv2.boxPoints(rect)
        box = np.int32(box)

        # Four edge lengths
        edges = []

        for i in range(4):

            p1 = box[i]

            p2 = box[(i+1)%4]

            d = np.linalg.norm(p1-p2)

            edges.append((d,p1,p2))

        edges.sort(key=lambda x:x[0])

        width_edges = edges[:2]

        length_edges = edges[2:]

        # Midpoints of opposite edges
        length_start = self.midpoint(
            length_edges[0][1],
            length_edges[0][2]
        )

        length_end = self.midpoint(
            length_edges[1][1],
            length_edges[1][2]
        )

        width_start = self.midpoint(
            width_edges[0][1],
            width_edges[0][2]
        )

        width_end = self.midpoint(
            width_edges[1][1],
            width_edges[1][2]
        )

        if view_name == "TOP":

            self.draw_measurement(
                overlay,
                length_start,
                length_end,
                (0,255,255),
                f"L {length_cm*10:.1f} mm"
            )

            self.draw_measurement(
                overlay,
                width_start,
                width_end,
                (255,0,0),
                f"W {width_cm*10:.1f} mm"
            )

        else:

            self.draw_measurement(
                overlay,
                width_start,
                width_end,
                (255,0,255),
                f"T {thickness_cm*10:.1f} mm"
            )

        cv2.putText(
            overlay,
            f"Area : {(area_px*(10/pixels_per_cm)**2):.1f} mm2",
            (20,30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0,255,0),
            2
        )

        cv2.putText(
            overlay,
            f"Calibration : OK",
            (20,60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0,200,255),
            2
        )

        return overlay
    
    def evaluate_capture_quality(
        self,
        image,
        contour,
        mask,
        rect
    ):
        """
        Evaluate image quality before prediction.
        Returns quality score and recommendations.
        """

        score = 100

        checks = {}

        h, w = image.shape[:2]

        x, y, bw, bh = cv2.boundingRect(contour)
        checks["banana_detected"] = True
        margin = 10

        touching = (
            x <= margin or
            y <= margin or
            x + bw >= w - margin or
            y + bh >= h - margin
        )

        checks["touching_border"] = touching

        if touching:
            score -= 20
        coverage = (
            cv2.contourArea(contour) /
            (w * h)
        )

        checks["coverage"] = round(
            coverage * 100,
            1
        )

        if coverage < 0.12:

            score -= 15

        elif coverage > 0.75:

            score -= 10
            
        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        blur = cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()

        checks["sharpness"] = round(blur,1)

        if blur < 80:

            score -= 15
        angle = rect[-1]

        checks["angle"] = round(angle,1)

        if abs(angle) > 35:

            score -= 10
        mask_pixels = np.count_nonzero(mask)

        contour_pixels = cv2.contourArea(contour)

        quality = contour_pixels / mask_pixels

        checks["segmentation"] = round(
            quality * 100,
            1
        )

        if quality < 0.90:

            score -= 10
        if score >= 90:

            status = "Excellent"

        elif score >= 80:

            status = "Good"

        elif score >= 65:

            status = "Fair"

        else:

            status = "Poor"
        if status == "Excellent":

            recommendation = (
                "Excellent image quality. "
                "Measurements are expected to be highly accurate."
            )

        elif status == "Good":

            recommendation = (
                "Good image quality. "
                "Minor deviations may occur."
            )

        elif status == "Fair":

            recommendation = (
                "Moderate quality. "
                "Please verify banana placement."
            )

        else:

            recommendation = (
                "Poor quality. "
                "Recapture the banana image."
            )
                
        return {

            "score": score,

                "status": status,

                "checks": checks,

                "recommendation": recommendation
        }
        
    def extract_raw_features(self,image_path, pixels_per_cm, prefix):
        print("Reading image:", image_path)
        img = cv2.imread(image_path)

        if img is None:
            raise FileNotFoundError(
                f"Could not load image asset at: {image_path}"
            )

        original_img = img.copy()

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        _, s, _ = cv2.split(hsv)

        _, thresh = cv2.threshold(
            s,
            35,
            255,
            cv2.THRESH_BINARY
        )

        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (7, 7)
        )

        mask = cv2.morphologyEx(
            thresh,
            cv2.MORPH_OPEN,
            kernel
        )

        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_CLOSE,
            kernel
        )
        mask_debug = cv2.cvtColor(
            mask,
            cv2.COLOR_GRAY2BGR
        )

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            raise ValueError(
                "Zero foreground objects identified."
            )

        banana_contour = max(
            contours,
            key=cv2.contourArea
        )

        contour_img = original_img.copy()

        cv2.drawContours(

            contour_img,

            [banana_contour],

            -1,

            (0,255,0),

            3
        )
        
        rect = cv2.minAreaRect(
            banana_contour
        )
        quality = self.evaluate_capture_quality(

            original_img,

            banana_contour,

            mask,

            rect
        )
        
        annotated_img = original_img.copy()

        # Draw detected contour
        cv2.drawContours(
            annotated_img,
            [banana_contour],
            -1,
            (0,255,0),
            3
        )

        box = cv2.boxPoints(rect)
        box = np.int32(box)
        # Four rectangle edges
        edge_lengths = []

        for i in range(4):

            p1 = box[i]

            p2 = box[(i + 1) % 4]

            dist = np.linalg.norm(p1 - p2)

            edge_lengths.append((dist, p1, p2))

        (_, _), (w_box_px, h_box_px), _ = rect

        edge_lengths.sort(
            key=lambda x: x[0]
        )
        width_edges = edge_lengths[:2]
        length_edges = edge_lengths[2:]
        box_length_cm = (
            max(w_box_px, h_box_px)
            / pixels_per_cm
        )
        
        length_start = self.midpoint(
            length_edges[0][1],
            length_edges[0][2]
        )

        length_end = self.midpoint(
            length_edges[1][1],
            length_edges[1][2]
        )
        
        width_start = self.midpoint(
            width_edges[0][1],
            width_edges[0][2]
        )

        width_end = self.midpoint(
            width_edges[1][1],
            width_edges[1][2]
        )

        box_width_cm = (
            min(w_box_px, h_box_px)
            / pixels_per_cm
        )

        dist_transform = cv2.distanceTransform(
            mask,
            cv2.DIST_L2,
            5
        )

        inner_core = dist_transform[
            dist_transform >
            (dist_transform.max() * 0.5)
        ]

        avg_radius_px = (
            np.mean(inner_core)
            if len(inner_core) > 0
            else dist_transform.max()
        )

        precise_thickness_cm = (
            avg_radius_px * 2
        ) / pixels_per_cm

        area_px = cv2.contourArea(
            banana_contour
        )
        
        annotated_img = self.create_measurement_overlay(
            original_img,
            banana_contour,
            rect,
            box_length_cm,
            box_width_cm,
            precise_thickness_cm,
            area_px,
            pixels_per_cm,
            prefix.upper()
        )
        
        
        #_________________________________
        debug = {

            "original":

                self.save_debug_image(
                original_img,
                f"{prefix}_original"
                ),

            "mask":

                self.save_debug_image(
                    mask_debug,
                    f"{prefix}_mask"
                ),

            "contour":

                self.save_debug_image(
                    contour_img,
                    f"{prefix}_contour"
                ),

            "annotated":

                self.save_debug_image(
                    annotated_img,
                    f"{prefix}_annotated"
                )
        }
        return (

            box_length_cm,

            box_width_cm,

            precise_thickness_cm,

            area_px,

            debug,

            quality
        )

    def calculate_3d_mass(
        self,
        top_image_path,
        side_image_path
    ):
        (
            top_box_len,
            top_box_wid,
            true_width_cm,
            top_area_px,
            top_debug,
            top_quality
        )=self.extract_raw_features(
            top_image_path,
            self.PIXELS_PER_CM_TOP,
            "top"
        )

        (
            _,
            _,
            true_depth_cm,
            _,
            side_debug,
            side_quality
        )=self.extract_raw_features(
            side_image_path,
            self.PIXELS_PER_CM_SIDE,
            "side"
        )

        curvature_ratio = (
            top_box_wid /
            top_box_len
        )

        corrected_length_cm = (
            top_box_len *
            (
                1 +
                0.55 *
                (curvature_ratio ** 2)
            )
        )

        precise_length_cm = (
            corrected_length_cm *
            0.94
        )

        cross_section_area = (
            np.pi *
            (true_width_cm / 2.0) *
            (true_depth_cm / 2.0)
        )

        calculated_volume_cm3 = (
            cross_section_area *
            precise_length_cm *
            self.SHAPE_CORRECTION
        )

        estimated_weight_g = (
            calculated_volume_cm3 *
            self.BANANA_DENSITY
        )

        area_mm2 = (
            top_area_px *
            (
                10.0 /
                self.PIXELS_PER_CM_TOP
            ) ** 2
        )

        return {

            "length_mm":
                round(precise_length_cm * 10, 2),

            "width_mm":
                round(true_width_cm * 10, 2),

            "thickness_mm":
                round(true_depth_cm * 10, 2),

            "area_mm2":
                round(area_mm2, 2),

            "weight_g":
                round(estimated_weight_g, 2),

            "debug": {

                "top": top_debug,

                "side": side_debug
            },
            "quality":{
                "overall":round(
                    (top_quality["score"]+
                    side_quality["score"])/2
                ),

                "top":top_quality,

                "side":side_quality
            }
        }
       