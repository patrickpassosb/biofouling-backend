import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
import os

# Define features based on the notebook analysis and user requirements
FEATURES = [
    "voyage_duration_days",
    "avg_speed",
    "distance_traveled",
    "port_time_ratio",
    "fuel_consumption",
    "temperature_avg",
    "last_cleaning_days"
]

def train_mock_model():
    print("Generating mock data...")
    # Generate synthetic data
    n_samples = 1000
    data = {
        "voyage_duration_days": np.random.uniform(5, 30, n_samples),
        "avg_speed": np.random.uniform(10, 25, n_samples),
        "distance_traveled": np.random.uniform(1000, 10000, n_samples),
        "port_time_ratio": np.random.uniform(0, 0.5, n_samples),
        "fuel_consumption": np.random.uniform(20, 100, n_samples),
        "temperature_avg": np.random.uniform(10, 35, n_samples),
        "last_cleaning_days": np.random.randint(0, 365, n_samples)
    }
    
    X = pd.DataFrame(data)
    
    # Generate target (Biofouling Level: 0, 1, 2, 3)
    # Logic: Higher temp + longer time since cleaning + slower speed -> higher risk
    risk_score = (
        (X["temperature_avg"] / 35) * 0.3 + 
        (X["last_cleaning_days"] / 365) * 0.5 + 
        (1 - X["avg_speed"] / 25) * 0.2
    )
    
    y = pd.cut(risk_score, bins=[-np.inf, 0.3, 0.5, 0.7, np.inf], labels=[0, 1, 2, 3]).astype(int)
    
    print("Training model...")
    # Create a pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ]), FEATURES)
        ]
    )
    
    clf = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    clf.fit(X, y)
    
    # Save model
    output_path = "app/ml_model/model.joblib"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump(clf, output_path)
    print(f"Model saved to {output_path}")

if __name__ == "__main__":
    train_mock_model()
