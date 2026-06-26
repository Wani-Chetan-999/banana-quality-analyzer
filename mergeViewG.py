import cv2
import numpy as np

# =========================================================================
# SYSTEM CALIBRATION CONSTANTS
# =========================================================================
PIXELS_PER_CM_TOP = 120.0   # Baseline scale for 25cm top-down view
PIXELS_PER_CM_SIDE = 110.0  # Baseline scale for 0-degree side view (adjust this!)

BANANA_DENSITY = 0.96       # Average density of fresh banana (g/cm³)
SHAPE_CORRECTION = 0.78     # Accounting for tapering ends of the fruit
# =========================================================================

def extract_raw_features(image_path, pixels_per_cm):
    """Isolates the banana and extracts precise baseline dimensions in cm."""
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image {image_path}")
        return None, None, None

    # 1. Isolate banana using Saturation channel
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    _, s, _ = cv2.split(hsv)
    _, thresh = cv2.threshold(s, 35, 255, cv2.THRESH_BINARY)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 2. Get Bounding Box Measurements
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, None, None
    banana_contour = max(contours, key=cv2.contourArea)
    
    rect = cv2.minAreaRect(banana_contour)
    (_, _), (w_box_px, h_box_px), _ = rect
    
    box_length_cm = max(w_box_px, h_box_px) / pixels_per_cm
    box_width_cm = min(w_box_px, h_box_px) / pixels_per_cm

    # 3. Get Precise Thickness/Diameter via Distance Transform
    dist_transform = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    inner_core = dist_transform[dist_transform > (dist_transform.max() * 0.5)]
    avg_radius_px = np.mean(inner_core) if len(inner_core) > 0 else dist_transform.max()
    precise_thickness_cm = (avg_radius_px * 2) / pixels_per_cm

    return box_length_cm, box_width_cm, precise_thickness_cm

def calculate_banana_3d_metrics(top_img_path, side_img_path):
    print("Processing Top-Down View...")
    top_box_len, top_box_wid, true_width_cm = extract_raw_features(top_img_path, PIXELS_PER_CM_TOP)
    
    print("Processing Side View (0 Degree)...")
    _, _, true_depth_cm = extract_raw_features(side_img_path, PIXELS_PER_CM_SIDE)

    if None in [top_box_len, true_width_cm, true_depth_cm]:
        print("Error processing one or both images. Please check your image inputs.")
        return

    # =========================================================================
    # 3D GEOMETRIC MATH ENGINE
    # =========================================================================
    # 1. Calculate Arc Length dynamically based on top-down curvature profile
    curvature_ratio = top_box_wid / top_box_len
    corrected_length_cm = top_box_len * (1 + 0.55 * (curvature_ratio ** 2))
    precise_length_cm = corrected_length_cm * 0.94  # Perspective compensation

    # 2. 3D Elliptical Cross-Section Volume Calculation
    # Area of ellipse = pi * radius_width * radius_depth
    cross_section_area = np.pi * (true_width_cm / 2.0) * (true_depth_cm / 2.0)
    
    # Total Volume = Cross-sectional area * Length * Shape optimization factor
    calculated_volume_cm3 = cross_section_area * precise_length_cm * SHAPE_CORRECTION

    # 3. Mass Estimation (Weight = Volume * Density)
    estimated_weight_g = calculated_volume_cm3 * BANANA_DENSITY

    # =========================================================================
    # DISPLAY METRICS REPORT
    # =========================================================================
    print(f"\n==================================================")
    print(f" 🍌 DUAL-VIEW 3D GRADING REPORT")
    print(f"==================================================")
    print(f"• True Curved Length   : {precise_length_cm:.2f} cm")
    print(f"• Horizontal Width     : {true_width_cm:.2f} cm (Top Profile)")
    print(f"• Vertical Depth       : {true_depth_cm:.2f} cm (Side Profile)")
    print(f"• Calculated 3D Volume : {calculated_volume_cm3:.2f} cm³")
    print(f"--------------------------------------------------")
    print(f"👉 ESTIMATED WEIGHT    : {estimated_weight_g:.2f} grams")
    print(f"==================================================")

if __name__ == "__main__":
    # Update these paths to your actual local file names
    calculate_banana_3d_metrics("D:\\Projects\\banana_grading_system\\media\\banana_images\\topView.jpeg", "D:\\Projects\\banana_grading_system\\media\\banana_images\\sideView.jpeg")
