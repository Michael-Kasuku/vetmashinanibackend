# Standard library imports
import os
import pickle
import json

# Third-party imports
import numpy as np
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from geopy.distance import geodesic
from django.contrib.auth.hashers import make_password, check_password

# Local app imports
from .models import User, VeterinarianProfile, FarmerProfile, Appointment, Notification, Favorite, Rating

# Django timezone import
from django.utils import timezone

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Basic fields for user creation
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        is_farmer = data.get('is_farmer', False)
        is_vet = data.get('is_vet', False)
        location_lat = data.get('location_lat', None)
        location_lng = data.get('location_lng', None)
        
        # Check if user with the same username or email exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already taken."}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already in use."}, status=400)
        
        # Create the user object
        user = User(
            username=username,
            email=email,
            password=make_password(password),  # Hash the password before saving
            is_farmer=is_farmer,
            is_vet=is_vet,
            location_lat=location_lat,
            location_lng=location_lng
        )
        
        user.save()

        # Create related profile based on user type
        if is_vet:
            VeterinarianProfile.objects.create(user=user)
        elif is_farmer:
            FarmerProfile.objects.create(user=user)

        return JsonResponse({"message": "User created successfully!"}, status=201)

    elif request.method == 'PUT':
        data = json.loads(request.body)
        
        # Retrieve the user by the user ID or username (authentication needed)
        user_id = data.get('user_id')
        user = User.objects.filter(id=user_id).first()

        if not user:
            return JsonResponse({"error": "User not found."}, status=404)
        
        # Update basic user fields
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        location_lat = data.get('location_lat')
        location_lng = data.get('location_lng')

        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.password = make_password(password)  # Hash the new password
        if location_lat is not None:
            user.location_lat = location_lat
        if location_lng is not None:
            user.location_lng = location_lng
        
        user.save()

        # Update profile-specific fields for veterinarians or farmers
        if user.is_vet:
            vet_profile = VeterinarianProfile.objects.filter(user=user).first()
            if vet_profile:
                certification_id = data.get('certification_id')
                bio = data.get('bio')
                if certification_id:
                    vet_profile.certification_id = certification_id
                if bio:
                    vet_profile.bio = bio
                vet_profile.save()

        elif user.is_farmer:
            farmer_profile = FarmerProfile.objects.filter(user=user).first()
            if farmer_profile:
                farm_name = data.get('farm_name')
                if farm_name:
                    farmer_profile.farm_name = farm_name
                farmer_profile.save()

        return JsonResponse({"message": "Profile updated successfully!"}, status=200)

    elif request.method == 'PATCH':
        data = json.loads(request.body)
        
        # Retrieve the user by the user ID or username (authentication needed)
        user_id = data.get('user_id')
        user = User.objects.filter(id=user_id).first()

        if not user:
            return JsonResponse({"error": "User not found."}, status=404)
        
        # Partially update user fields (only the ones that are present in the request)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        location_lat = data.get('location_lat')
        location_lng = data.get('location_lng')

        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.password = make_password(password)  # Hash the new password
        if location_lat is not None:
            user.location_lat = location_lat
        if location_lng is not None:
            user.location_lng = location_lng
        
        user.save()

        # Partially update profile-specific fields for veterinarians or farmers
        if user.is_vet:
            vet_profile = VeterinarianProfile.objects.filter(user=user).first()
            if vet_profile:
                certification_id = data.get('certification_id')
                bio = data.get('bio')
                if certification_id:
                    vet_profile.certification_id = certification_id
                if bio:
                    vet_profile.bio = bio
                vet_profile.save()

        elif user.is_farmer:
            farmer_profile = FarmerProfile.objects.filter(user=user).first()
            if farmer_profile:
                farm_name = data.get('farm_name')
                if farm_name:
                    farmer_profile.farm_name = farm_name
                farmer_profile.save()

        return JsonResponse({"message": "Profile updated successfully!"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        username = data.get('username')
        password = data.get('password')

        # Authenticate user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid username or password."}, status=400)

        # Check if the password matches
        if not check_password(password, user.password):
            return JsonResponse({"error": "Invalid username or password."}, status=400)

        # If successful, return user info (you can add a token for authentication here)
        response_data = {
            "username": user.username,
            "email": user.email,
            "is_farmer": user.is_farmer,
            "is_vet": user.is_vet,
            "location_lat": user.location_lat,
            "location_lng": user.location_lng
        }

        return JsonResponse({"message": "Login successful", "user": response_data}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
def appointments(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        role = request.GET.get('role')  # 'farmer' or 'vet'

        if not user_id or not role:
            return HttpResponseBadRequest("Missing user_id or role")

        user = get_object_or_404(User, pk=user_id)
        if role == 'farmer':
            appointments = Appointment.objects.filter(farmer=user).order_by('-appointment_date')
        else:
            appointments = Appointment.objects.filter(vet=user).order_by('-appointment_date')

        data = [
            {
                'id': a.id,
                'farmer': a.farmer.username,
                'vet': a.vet.username,
                'appointment_date': a.appointment_date,
                'status': a.status,
                'location_lat': a.location_lat,
                'location_lng': a.location_lng,
                'farmer_note': a.farmer_note,
                'vet_note': a.vet_note,
                'vet_status_updated_at': a.vet_status_updated_at,  # Include the new field
            } for a in appointments
        ]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        data = json.loads(request.body)
        try:
            farmer = User.objects.get(pk=data['farmer_id'])
            vet = User.objects.get(pk=data['vet_id'])
            appointment = Appointment.objects.create(
                farmer=farmer,
                vet=vet,
                appointment_date=data['appointment_date'],
                location_lat=data.get('location_lat'),
                location_lng=data.get('location_lng'),
                farmer_note=data.get('farmer_note', '')
            )
            # Send notification to vet about the new appointment
            Notification.objects.create(
                recipient=vet,
                message=f"New appointment created with {farmer.username}"
            )
            # Send notification to farmer about the new appointment
            Notification.objects.create(
                recipient=farmer,
                message=f"Your appointment with {vet.username} has been scheduled."
            )
            return JsonResponse({'message': 'Appointment created', 'id': appointment.id})
        except Exception as e:
            return HttpResponseBadRequest(str(e))

    elif request.method == 'PUT':
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')
        status = data.get('status')
        vet_note = data.get('vet_note')
        vet_id = data.get('vet_id')

        if not appointment_id or not status or not vet_note or not vet_id:
            return HttpResponseBadRequest("Missing appointment_id, status, vet_note, or vet_id.")

        # Ensure the appointment exists
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Ensure the vet is the one updating the appointment
        if appointment.vet.id != vet_id:
            return JsonResponse({"error": "This is not your appointment to update."}, status=403)

        # Update the status and vet's note
        appointment.status = status
        appointment.vet_note = vet_note
        
        # Set the timestamp when vet accepts or cancels the appointment
        if status in ['accepted', 'cancelled']:
            appointment.vet_status_updated_at = timezone.now()  # Set the timestamp

        appointment.save()

        # Send notification to the farmer about the updated appointment
        Notification.objects.create(
            recipient=appointment.farmer,
            message=f"Your appointment with {appointment.vet.username} has been updated. Status: {status}"
        )

        return JsonResponse({'message': 'Appointment updated successfully', 'id': appointment.id})

    return HttpResponseNotAllowed(['GET', 'POST', 'PUT'])

@csrf_exempt
def notifications(request, user_id):
    if request.method == 'GET':
        notes = Notification.objects.filter(recipient_id=user_id).order_by('-created_at')
        data = [
            {
                'id': n.id,
                'message': n.message,
                'created_at': n.created_at,
                'is_read': n.is_read
            } for n in notes
        ]
        return JsonResponse(data, safe=False)

    return HttpResponseNotAllowed(['GET'])

@csrf_exempt
def favorites(request, user_id=None):
    if request.method == 'GET' and user_id:
        favs = Favorite.objects.filter(user_id=user_id)
        data = [
            {
                'id': f.id,
                'favorite_user_id': f.favorite_user.id,
                'favorite_user_username': f.favorite_user.username
            } for f in favs
        ]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        data = json.loads(request.body)
        try:
            user = User.objects.get(pk=data['user_id'])
            fav_user = User.objects.get(pk=data['favorite_user_id'])
            favorite, created = Favorite.objects.get_or_create(user=user, favorite_user=fav_user)
            if created:
                return JsonResponse({'message': 'Favorite added'})
            return JsonResponse({'message': 'Already favorited'})
        except Exception as e:
            return HttpResponseBadRequest(str(e))

    return HttpResponseNotAllowed(['GET', 'POST'])

@csrf_exempt
def rate_vet(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            appointment = Appointment.objects.get(pk=data['appointment_id'])
            farmer = User.objects.get(pk=data['farmer_id'])
            vet = User.objects.get(pk=data['vet_id'])

            Rating.objects.create(
                appointment=appointment,
                farmer=farmer,
                vet=vet,
                rating=data['rating'],
                review=data.get('review', '')
            )
            return JsonResponse({'message': 'Rating submitted'})
        except Exception as e:
            return HttpResponseBadRequest(str(e))

    elif request.method == 'GET':
        vet_id = request.GET.get('vet_id')
        if not vet_id:
            return HttpResponseBadRequest("Missing vet_id parameter")

        try:
            vet = User.objects.get(pk=vet_id)
            ratings = Rating.objects.filter(vet=vet)

            data = [
                {
                    'appointment_id': r.appointment.id,
                    'farmer': r.farmer.username,
                    'rating': r.rating,
                    'review': r.review,
                    'created_at': r.created_at
                } for r in ratings
            ]
            return JsonResponse(data, safe=False)

        except User.DoesNotExist:
            return HttpResponseBadRequest("Vet not found")
        except Exception as e:
            return HttpResponseBadRequest(str(e))

    return HttpResponseNotAllowed(['GET', 'POST'])

@csrf_exempt
def nearby_vets(request):
    if request.method == 'GET':
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        if not lat or not lng:
            return HttpResponseBadRequest("Missing coordinates")

        lat, lng = float(lat), float(lng)
        all_vets = User.objects.filter(is_vet=True, location_lat__isnull=False, location_lng__isnull=False)

        data = []
        for vet in all_vets:
            distance = geodesic((lat, lng), (vet.location_lat, vet.location_lng)).km
            if distance <= 50:
                data.append({
                    'id': vet.id,
                    'username': vet.username,
                    'email': vet.email,
                    'distance_km': round(distance, 2)
                })
        return JsonResponse(data, safe=False)

    return HttpResponseNotAllowed(['GET'])

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
