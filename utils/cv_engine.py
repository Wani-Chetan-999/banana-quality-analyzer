# utils/cv_engine.py
import cv2
import numpy as np
import logging

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

    def extract_raw_features(self, image_path, pixels_per_cm):
        print("Reading image:", image_path)

        img = cv2.imread(image_path)

        if img is None:
            raise FileNotFoundError(f"Could not load image asset at: {image_path}")

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

        rect = cv2.minAreaRect(
            banana_contour
        )

        (_, _), (w_box_px, h_box_px), _ = rect

        box_length_cm = (
            max(w_box_px, h_box_px)
            / pixels_per_cm
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

        return (
            box_length_cm,
            box_width_cm,
            precise_thickness_cm,
            area_px
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
            top_area_px
        ) = self.extract_raw_features(
            top_image_path,
            self.PIXELS_PER_CM_TOP
        )

        (
            _,
            _,
            true_depth_cm,
            _
        ) = self.extract_raw_features(
            side_image_path,
            self.PIXELS_PER_CM_SIDE
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
                round(
                    precise_length_cm * 10,
                    2
                ),

            "width_mm":
                round(
                    true_width_cm * 10,
                    2
                ),

            "thickness_mm":
                round(
                    true_depth_cm * 10,
                    2
                ),

            "area_mm2":
                round(
                    area_mm2,
                    2
                ),

            "weight_g":
                round(
                    estimated_weight_g,
                    2
                )
        }
       