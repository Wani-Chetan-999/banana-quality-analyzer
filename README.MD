# 🍌 Banana Quality Analyzer

A Computer Vision and Machine Learning-based web application for automated banana measurement, weight estimation, and quality grading using image processing techniques.

---

# 📖 Overview

The Banana Quality Analyzer is designed to estimate the physical characteristics of a banana from images captured using two camera views:

* **Top View** – Measures length, width, and projected area.
* **Side View** – Measures thickness.

These measurements are combined to estimate the banana's weight and assign a quality grade (A, B, or C).

The project aims to reduce manual inspection, improve grading consistency, and provide an efficient solution for agricultural quality assessment.

---

# ✨ Features

* Image upload for Top View and Side View
* Automatic banana segmentation using OpenCV
* Image preprocessing and noise removal
* Contour detection
* Length, Width, Thickness measurement
* Projected Area calculation
* Weight estimation using geometric measurements
* Automatic Grade Prediction (A/B/C)
* Result visualization with measured dimensions
* Admin panel for grading threshold configuration
* REST API support

---

# 🧠 Technologies Used

## Backend

* Python
* Django
* Django REST Framework

## Computer Vision

* OpenCV
* NumPy

## Machine Learning

* Scikit-learn
* Random Forest Regression (for weight prediction)

## Database

* SQLite

## Frontend

* HTML
* CSS
* JavaScript
* Bootstrap

---

# 🔬 Computer Vision Pipeline

1. Upload banana images
2. Image preprocessing
3. Background removal
4. Image thresholding
5. Morphological operations
6. Contour detection
7. Largest contour extraction
8. Bounding rectangle calculation
9. Pixel-to-mm calibration
10. Length measurement
11. Width measurement
12. Thickness measurement
13. Projected area calculation
14. Weight estimation
15. Grade prediction

---

# 🤖 Machine Learning Workflow

* Image Acquisition
* Image Preprocessing
* Feature Extraction
* Measurement Calibration
* Weight Estimation
* Grade Classification

---

# 📊 Extracted Features

* Banana Length
* Banana Width
* Banana Thickness
* Projected Area
* Estimated Volume
* Estimated Weight

---

# 🏷️ Grade Classification

The estimated weight is compared against configurable grading thresholds.

Example:

| Grade | Weight Range    |
| ----- | --------------- |
| A     | Highest Quality |
| B     | Medium Quality  |
| C     | Lower Quality   |

Thresholds can be modified through the Django Admin Panel.

---

# 📂 Project Structure

```text
Banana_Quality_Analyzer/
│
├── api/
├── core_app/
├── templates/
├── static/
├── media/
├── utils/
├── models/
├── ml_engine.py
├── cv_engine.py
├── manage.py
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

Clone the repository

```bash
git clone <repository-url>
```

Navigate into the project

```bash
cd Banana_Quality_Analyzer
```

Create virtual environment

```bash
python -m venv venv
```

Activate environment

Windows

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run migrations

```bash
python manage.py migrate
```

Create superuser

```bash
python manage.py createsuperuser
```

Run the server

```bash
python manage.py runserver
```

---

# 📡 API Workflow

1. Upload Top View Image
2. Upload Side View Image
3. Image Processing
4. Measurement Extraction
5. Weight Estimation
6. Grade Prediction
7. JSON Response

---

# 📈 Future Improvements

* Deep Learning-based segmentation
* Automatic camera calibration
* Multi-object detection
* Ripeness detection
* Defect detection
* Disease detection
* Mobile application
* Real-time camera integration
* Cloud deployment
* Explainable AI (XAI)

---

# 📚 Key Algorithms & Techniques

* Image Preprocessing
* Gaussian Blur
* Thresholding
* Morphological Operations
* Contour Detection
* Bounding Rectangle
* Pixel Calibration
* Feature Extraction
* Geometric Measurement
* Random Forest Regression
* Rule-based Grade Classification

---

# 🎯 Applications

* Fruit Quality Inspection
* Agricultural Automation
* Packing Industries
* Food Processing Units
* Research & Education

---
# 📄 License

This project is developed for educational and research purposes.
