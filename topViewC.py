import cv2
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================

IMAGE_PATH = r"D:\Projects\banana_grading_system\media\banana_images\topView.jpeg"

# HSV Range for Yellow Banana
LOWER_YELLOW = np.array([15, 40, 70])
UPPER_YELLOW = np.array([45, 255, 255])

MIN_CONTOUR_AREA = 10000

MAX_DISPLAY_WIDTH = 1200
MAX_DISPLAY_HEIGHT = 800

# ============================================================

image = cv2.imread(IMAGE_PATH)

if image is None:
    raise Exception("Unable to load image.")

original = image.copy()

height, width = image.shape[:2]

print(f"\nImage Size : {width} x {height}")

# ============================================================
# Convert to HSV
# ============================================================

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

mask = cv2.inRange(hsv, LOWER_YELLOW, UPPER_YELLOW)

# ============================================================
# Morphological Cleaning
# ============================================================

kernel = cv2.getStructuringElement(
    cv2.MORPH_ELLIPSE,
    (9, 9)
)

mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

# ============================================================
# Find Contours
# ============================================================

contours, _ = cv2.findContours(
    mask,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

valid_contours = []

for c in contours:

    area = cv2.contourArea(c)

    if area > MIN_CONTOUR_AREA:
        valid_contours.append(c)

print(f"Contours Found : {len(contours)}")
print(f"Valid Contours : {len(valid_contours)}")

if len(valid_contours) == 0:
    raise Exception("No Banana Detected")

banana = max(valid_contours, key=cv2.contourArea)

# ============================================================
# Measurements
# ============================================================
from skimage.morphology import skeletonize
from scipy.ndimage import distance_transform_edt

# Create binary image from contour
binary = np.zeros(mask.shape, dtype=np.uint8)

cv2.drawContours(binary, [banana], -1, 255, -1)

# Skeleton
skeleton = skeletonize(binary > 0)

# -------------------------------
# Curved Length
# -------------------------------

points = np.column_stack(np.where(skeleton))

length_px = 0

for i in range(len(points)-1):

    p1 = points[i]
    p2 = points[i+1]

    length_px += np.linalg.norm(p1-p2)

# -------------------------------
# Width using Distance Transform
# -------------------------------

distance = distance_transform_edt(binary)

width_px = distance.max() * 2

# ============================================================
# Centroid
# ============================================================

M = cv2.moments(banana)

if M["m00"] != 0:
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
else:
    cx, cy = 0, 0

# ============================================================
# Draw Results
# ============================================================

cv2.drawContours(original, [banana], -1, (0, 255, 0), 4)

# cv2.drawContours(original, [box], 0, (255, 0, 0), 3)

cv2.circle(original, (cx, cy), 6, (0, 0, 255), -1)

# Bounding Rectangle

x, y, w_box, h_box = cv2.boundingRect(banana)

cv2.rectangle(
    original,
    (x, y),
    (x + w_box, y + h_box),
    (255, 255, 0),
    2
)

# ============================================================
# Put Text
# ============================================================

cv2.putText(
    original,
    f"Length : {length_px:.2f}px",
    (20, 40),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.9,
    (0, 0, 255),
    2
)

cv2.putText(
    original,
    f"Width : {width_px:.2f}px",
    (20, 80),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.9,
    (0, 0, 255),
    2
)

cv2.putText(
    original,
    f"Area : {area:.0f}px^2",
    (20, 120),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.9,
    (0, 0, 255),
    2
)

# ============================================================
# Console Output
# ============================================================

print("\n==============================")
print("BANANA DETECTED")
print("==============================")

print(f"Length      : {length_px:.2f} px")
print(f"Width       : {width_px:.2f} px")
print(f"Area        : {area:.2f} px²")
# print(f"Perimeter   : {perimeter:.2f} px")

print("==============================\n")

# ============================================================
# Resize for Display
# ============================================================

scale = min(
    MAX_DISPLAY_WIDTH / width,
    MAX_DISPLAY_HEIGHT / height
)

display = cv2.resize(
    original,
    None,
    fx=scale,
    fy=scale
)

display_mask = cv2.resize(
    mask,
    None,
    fx=scale,
    fy=scale
)

# ============================================================
# Save Result
# ============================================================

cv2.imwrite("result_detection.jpg", original)

# ============================================================
# Show
# ============================================================

cv2.imshow("HSV Mask", display_mask)
cv2.imshow("Banana Detection", display)

cv2.waitKey(0)
cv2.destroyAllWindows()


print(f"Curved Length : {length_px:.2f} px")
print(f"Maximum Width : {width_px:.2f} px")


MM_PER_PIXEL = 185 / length_px

length_mm = length_px * MM_PER_PIXEL

width_mm = width_px * MM_PER_PIXEL

area_mm2 = area * (MM_PER_PIXEL ** 2)
skeleton_img = np.zeros_like(binary)

skeleton_img[skeleton] = 255

cv2.imshow("Skeleton", skeleton_img)