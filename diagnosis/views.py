import os
import pickle
import numpy as np
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def predict_disease(request):
    if request.method == 'POST':
        try:
            data = request.POST.getlist('symptoms[]')  # Expecting a list of symptoms
            
            model_file = os.path.join(settings.BASE_DIR, 'diagnosis/model.pkl')
            if not os.path.exists(model_file):
                return JsonResponse({"error": "Model file not found"}, status=500)
            
            with open(model_file, 'rb') as f:
                model, scaler, feature_columns, disease_mapping = pickle.load(f)

            input_data = np.zeros(len(feature_columns))
            for symptom in data:
                if symptom in feature_columns:
                    input_data[feature_columns.index(symptom)] = 1

            input_data = scaler.transform([input_data])
            prediction = model.predict(input_data)
            disease_name = {v: k for k, v in disease_mapping.items()}[prediction[0]]

            return JsonResponse({"predicted_disease": disease_name})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)
