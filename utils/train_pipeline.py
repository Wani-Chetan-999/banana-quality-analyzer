import os
import sys
import logging
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core_app.settings")

import django
django.setup()
from django.conf import settings

# Initialize Django environment handles if executed as standalone script
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core_app.settings")
    import django
    django.setup()

from utils.ml_engine import BananaMLEngine

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Banana Weight Regression Training Pipeline")
    parser.add_argument("--csv", type=str, required=True, help="Path to the compiled CSV training dataset")
    args = parser.parse_list = parser.parse_args()

    if not os.path.exists(args.csv):
        logger.error(f"Target training source data file not found: {args.csv}")
        sys.exit(1)

    logger.info("Initializing Random Forest Regressor initialization framework...")
    engine = BananaMLEngine()
    
    logger.info(f"Extracting features and streaming metrics from target matrix: {args.csv}")
    try:
        metrics = engine.train_model(args.csv)
        logger.info("======= MODEL TRAINING METRICS SUCCESS =======")
        logger.info(f"Mean Absolute Error (MAE) : {metrics['mae']} grams")
        logger.info(f"Root Mean Squared Error (RMSE): {metrics['rmse']} grams")
        logger.info(f"Coefficient of Determination (R²): {metrics['r2_score']}")
        logger.info(f"Binary artifacts successfully persisted to disk storage.")
    except Exception as ex:
        logger.error(f"Execution step pipeline failure encountered: {str(ex)}")
        sys.exit(1)

if __name__ == "__main__":
    main()