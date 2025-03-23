import os
import pickle
import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from django.conf import settings

class Command(BaseCommand):
    help = 'Train the Random Forest model and save it as a pickle file'

    def handle(self, *args, **kwargs):
        # Load training data
        data_path = os.path.join(settings.BASE_DIR, 'diagnosis/training.csv')
        df = pd.read_csv(data_path)
        
        # Prepare features and labels
        feature_columns = df.drop(columns=['prognosis']).columns.tolist()
        disease_mapping = {disease: idx for idx, disease in enumerate(df['prognosis'].unique())}
        df['prognosis'] = df['prognosis'].map(disease_mapping)
        
        X = df[feature_columns]
        y = df['prognosis']

        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)

        # Save trained model
        model_file = os.path.join(settings.BASE_DIR, 'diagnosis/model.pkl')
        with open(model_file, 'wb') as f:
            pickle.dump((model, scaler, feature_columns, disease_mapping), f)
        
        # Model evaluation
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        self.stdout.write(self.style.SUCCESS(f'Model trained and saved successfully with accuracy: {accuracy * 100:.2f}%'))
