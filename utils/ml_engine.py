import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from django.conf import settings

class BananaMLEngine:
    """Manages the lifecycle of the regression model for mass prediction."""
    def __init__(self):
        self.model_dir = os.path.join(settings.BASE_DIR, 'trained_models')
        os.makedirs(self.model_dir, exist_ok=True)
        self.model_path = os.path.join(self.model_dir, 'banana_rf_regressor.joblib')
        self.model = self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            return joblib.load(self.model_path)
        return None

    def train_model(self, csv_data_path: str) -> dict:
        """Trains model parsing clean data vectors directly out of the provided CSV headers."""
        df = pd.read_csv(csv_data_path)
        
        # Strip trailing and leading white spaces from column header names
        df.columns = df.columns.str.strip()
        
        # Drop rows where critical parameters or labels are missing
        df = df.dropna(subset=['Wt (gm)', 'L', 'W', 'T', 'V1'])
        
        # Ensure values are strictly parsed as float elements
        for col in ['L', 'W', 'T', 'V1', 'Wt (gm)']:
            df[col] = df[col].astype(float)
            
        features = ['L', 'W', 'T', 'V1']
        X = df[features]
        y = df['Wt (gm)']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        regressor = RandomForestRegressor(n_estimators=150, max_depth=12, random_state=42)
        regressor.fit(X_train, y_train)
        
        # Performance Evaluation Metrics
        predictions = regressor.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        r2 = r2_score(y_test, predictions)
        
        # Save model state
        joblib.dump(regressor, self.model_path)
        self.model = regressor
        
        return {"mae": round(mae, 3), "rmse": round(rmse, 3), "r2_score": round(r2, 3)}

    def predict_weight(self, length: float, width: float, thickness: float, area: float) -> float:
        """Executes inference via the trained model runtime matrix."""
        if not self.model:
            raise RuntimeError("Inference model missing or not yet initialized.")
        
        input_data = np.array([[length, width, thickness, area]])
        prediction = self.model.predict(input_data)
        return float(prediction[0])