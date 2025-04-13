# Standard library imports
import os
import pickle
import json

# Third-party imports
import numpy as np
from django.conf import settings
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from geopy.distance import geodesic
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q

# Local app imports
from .models import User,CertifiedVet, VeterinarianProfile, FarmerProfile, Appointment, Notification, Favorite, CoinReward, PlatformCoin

# Django timezone import
from django.utils import timezone

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        # Extract fields
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        is_farmer = data.get('is_farmer', False)
        is_vet = data.get('is_vet', False)
        location_lat = data.get('location_lat')
        location_lng = data.get('location_lng')

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already taken."}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already in use."}, status=400)

        # If user is a vet, ensure email exists in CertifiedVet table
        if is_vet and not CertifiedVet.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email not found in Certified Veterinarians registry."}, status=403)

        # Determine coin bonus
        bonus_coins = 200 if is_vet else 100 if is_farmer else 0

        # Deduct coins from platform account
        try:
            platform = PlatformCoin.objects.first()
            if platform is None:
                return JsonResponse({"error": "PlatformCoin account not initialized."}, status=500)
            platform.subtract_coins(bonus_coins)
        except ValueError as ve:
            return JsonResponse({"error": str(ve)}, status=400)

        # Create the user
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_farmer=is_farmer,
            is_vet=is_vet,
            location_lat=location_lat,
            location_lng=location_lng
        )

        # Create related profile and reward
        if is_vet:
            VeterinarianProfile.objects.create(user=user)
        elif is_farmer:
            FarmerProfile.objects.create(user=user)

        CoinReward.objects.create(user=user, coins=bonus_coins)

        return JsonResponse({"message": "User created successfully!"}, status=201)

@csrf_exempt
def update_profile(request):
    if request.method == 'PATCH':
        data = json.loads(request.body)

        # Retrieve user by username
        username = data.get('username')
        user = User.objects.filter(username=username).first()

        if not user:
            return JsonResponse({"error": "User not found."}, status=404)

        # Extract location fields
        location_lat = data.get('location_lat')
        location_lng = data.get('location_lng')

        # Only allow updating of location fields
        if location_lat is not None:
            user.location_lat = location_lat
        if location_lng is not None:
            user.location_lng = location_lng

        # Save the updated user with new location data
        user.save()

        return JsonResponse({"message": "Location updated successfully!"}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
def vet_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        username = data.get('username')
        password = data.get('password')

        try:
            user = User.objects.get(username=username, is_vet=True)
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid vet credentials."}, status=400)

        if not check_password(password, user.password):
            return JsonResponse({"error": "Invalid password."}, status=400)

        response_data = {
            "username": user.username,
            "email": user.email,
            "is_vet": user.is_vet,
            "location_lat": user.location_lat,
            "location_lng": user.location_lng
        }

        return JsonResponse({"message": "Vet login successful", "user": response_data}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)

@csrf_exempt
def farmer_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        username = data.get('username')
        password = data.get('password')

        try:
            user = User.objects.get(username=username, is_farmer=True)
        except User.DoesNotExist:
            return JsonResponse({"error": "Invalid farmer credentials."}, status=400)

        if not check_password(password, user.password):
            return JsonResponse({"error": "Invalid password."}, status=400)

        response_data = {
            "username": user.username,
            "email": user.email,
            "is_farmer": user.is_farmer,
            "location_lat": user.location_lat,
            "location_lng": user.location_lng
        }

        return JsonResponse({"message": "Farmer login successful", "user": response_data}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@csrf_exempt
def appointments(request):
    if request.method == 'GET':
        username = request.GET.get('username')

        if not username:
            return HttpResponseBadRequest("Missing username")

        # Retrieve the user by username
        user = get_object_or_404(User, username=username)

        if user.is_farmer:
            appointments = Appointment.objects.filter(farmer=user).order_by('-time_sent')
        elif user.is_vet:
            appointments = Appointment.objects.filter(vet=user).order_by('-time_sent')
        else:
            return HttpResponseBadRequest("User is neither a farmer nor a vet")

        data = [
            {
                'id': a.id,
                'farmer': a.farmer.username,   
                'farmer_note': a.farmer_note,
                'status': a.status,
                'vet': a.vet.username,
                'vet_note': a.vet_note,
                'time_sent': a.time_sent,
            } for a in appointments
        ]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        data = json.loads(request.body)
        try:
            # Fetch the farmer and vet using their usernames
            farmer = User.objects.get(username=data['farmer_username'])
            vet = User.objects.get(username=data['vet_username'])

            # Handle coin balances
            farmer_coins, _ = CoinReward.objects.get_or_create(user=farmer)

            # Deduct 5 coins
            farmer_coins.subtract_coins(5)

            # Reward vet 2 coins
            vet_coins, _ = CoinReward.objects.get_or_create(user=vet)
            vet_coins.add_coins(2)

            # Add 3 coins to platform balance
            platform_coin, _ = PlatformCoin.objects.get_or_create(id=1)
            platform_coin.add_coins(3)

            # Create appointment with current timestamp
            appointment = Appointment.objects.create(
                farmer=farmer,
                vet=vet,
                farmer_note=data.get('farmer_note', '')
            )

            # Send notifications
            Notification.objects.create(
                recipient=vet,
                message=f"{farmer.username} has scheduled new appointment with you."
            )
            Notification.objects.create(
                recipient=farmer,
                message=f"Your appointment with {vet.username} has been scheduled."
            )

            return JsonResponse({'message': 'Appointment created', 'id': appointment.id})
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    elif request.method == 'PATCH':
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')
        status = data.get('status')
        vet_note = data.get('vet_note')
        vet_username = data.get('username')

        if not appointment_id or not status or not vet_note or not vet_username:
            return HttpResponseBadRequest("Missing appointment_id, status, vet_note, or vet_username.")

        # Get the vet user object
        vet = get_object_or_404(User, username=vet_username)

        # Ensure the user is a vet
        if not vet.is_vet:
            return JsonResponse({"error": "User is not a veterinarian."}, status=403)

        # Get the appointment
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Ensure this vet is the one assigned to the appointment
        if appointment.vet != vet:
            return JsonResponse({"error": "This is not your appointment to update."}, status=403)

        # Update appointment
        appointment.status = status
        appointment.vet_note = vet_note

        if status in ['approved', 'cancelled']:
            appointment.vet_status_updated_at = timezone.now()

        appointment.save()

        Notification.objects.create(
            recipient=appointment.farmer,
            message=f"Your appointment with {appointment.vet.username} has been updated. Status: {status}"
        )
        Notification.objects.create(
            recipient=appointment.vet,
            message=f"Your appointment with {appointment.farmer.username} has been updated. Status: {status}"
        )

        return JsonResponse({'message': 'Appointment updated successfully', 'id': appointment.id})


    return HttpResponseNotAllowed(['GET', 'POST', 'PUT'])

@csrf_exempt
def get_notifications(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    try:
        username = request.GET.get('username')  # Get the username from query parameters

        if not username:
            return JsonResponse({"error": "Username is required."}, status=400)
        
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponseNotFound("User not found")

    notes = Notification.objects.filter(recipient=user).order_by('-created_at')
    data = [
        {
            'id': n.id,
            'message': n.message,
            'created_at': n.created_at,
            'is_read': n.is_read
        } for n in notes
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
def mark_notification_as_read(request):
    if request.method == 'PATCH':
        try:
            # Parse the JSON body
            body = json.loads(request.body)
            notification_id = body.get('notification_id')

            # Get the notification object or return 404 if it doesn't exist
            notification = get_object_or_404(Notification, id=notification_id)

            # Mark the notification as read
            notification.is_read = True
            notification.save()

            # Return success response
            return JsonResponse({'status': 'success', 'message': 'Notification marked as read'})

        except Exception as e:
            # Handle error (invalid or missing notification ID)
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def nearby_vets(request):
    if request.method == 'GET':
        username = request.GET.get('username')
        if not username:
            return HttpResponseBadRequest("Missing username")

        try:
            user = User.objects.get(username=username, is_farmer=True)
            if user.location_lat is None or user.location_lng is None:
                return HttpResponseBadRequest("User location not set")
        except User.DoesNotExist:
            return HttpResponseBadRequest("Farmer not found")

        lat, lng = float(user.location_lat), float(user.location_lng)

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

"""
Reward System 
Deposit to wallet simply means get money from Mpesa
Withdraw from wallet simply means send money to mpesa
Deposit coins simply means get money from wallet
Withdraw coins simply means send money to wallet
"""
COIN_TO_KSH = 25
MIN_WITHDRAWAL_COINS = 50
MAX_DEPOSIT_COINS = 10000

@csrf_exempt
def deposit_coins(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method.")

    data = json.loads(request.body)
    username = data.get('username')
    deposit_coins = data.get('coins')

    if not username or deposit_coins is None:
        return HttpResponseBadRequest("Missing username or coins.")

    if deposit_coins > MAX_DEPOSIT_COINS:
        return JsonResponse({'error': f'Maximum of {MAX_DEPOSIT_COINS} coins allowed per deposit.'}, status=400)

    user = User.objects.filter(username=username).first()
    if not user:
        return JsonResponse({'error': 'User not found.'}, status=404)

    required_ksh = deposit_coins / COIN_TO_KSH
    if user.wallet_balance < required_ksh:
        return JsonResponse({'error': 'Insufficient wallet balance.'}, status=400)

    coin_reward, _ = CoinReward.objects.get_or_create(user=user)

    # Deduct from wallet and add coins
    user.wallet_balance -= required_ksh
    user.save()

    try:
        coin_reward.add_coins(deposit_coins)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    # ✅ Create notification
    Notification.objects.create(
        recipient=user,
        message=f"You deposited {deposit_coins} coins (KES {required_ksh:.2f}) from your wallet."
    )

    return JsonResponse({
        'message': f'{deposit_coins} coins deposited successfully.',
        'new_coin_balance': coin_reward.coins,
        'new_wallet_balance': user.wallet_balance
    })

@csrf_exempt
def withdraw_coins(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method.")

    data = json.loads(request.body)
    username = data.get('username')
    withdraw_coins = data.get('coins')

    if not username or withdraw_coins is None:
        return HttpResponseBadRequest("Missing username or coins amount.")

    if withdraw_coins < MIN_WITHDRAWAL_COINS:
        return JsonResponse({'error': f'Minimum withdrawal is {MIN_WITHDRAWAL_COINS} coins.'}, status=400)

    user = User.objects.filter(username=username).first()
    if not user:
        return JsonResponse({'error': 'User not found.'}, status=404)

    coin_reward, _ = CoinReward.objects.get_or_create(user=user)

    try:
        coin_reward.subtract_coins(withdraw_coins)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    withdrawn_ksh = withdraw_coins / COIN_TO_KSH

    # Update the user's wallet balance
    user.wallet_balance += withdrawn_ksh
    user.save()

    # ✅ Create notification
    Notification.objects.create(
        recipient=user,
        message=f"You withdrew {withdraw_coins} coins (KES {withdrawn_ksh:.2f}) to your wallet."
    )

    return JsonResponse({
        'message': f'{withdraw_coins} coins withdrawn successfully. You have received KES {withdrawn_ksh}.',
        'new_coin_balance': coin_reward.coins,
        'new_wallet_balance': user.wallet_balance
    })

@csrf_exempt
def get_wallet_balance(request):
    if request.method == 'GET':
        username = request.GET.get('username')  # Get the username from query parameters

        if not username:
            return JsonResponse({"error": "Username is required."}, status=400)

        try:
            user = User.objects.get(username=username)  # Fetch the user using the username
            return JsonResponse({"wallet_balance": user.wallet_balance}, status=200)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=404)

@csrf_exempt
def get_coin_balance(request):
    if request.method == 'GET':
        username = request.GET.get('username')  # Get the username from query parameters

        if not username:
            return JsonResponse({"error": "Username is required."}, status=400)

        try:
            user = User.objects.get(username=username)  # Fetch the user using the username
            coin_reward = CoinReward.objects.get(user=user)  # Fetch the CoinReward for the user
            return JsonResponse({"coin_balance": coin_reward.coins}, status=200)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=404)
        except CoinReward.DoesNotExist:
            return JsonResponse({"error": "Coin reward record not found."}, status=404)

@csrf_exempt
def favorite_vets(request):
    if request.method == 'GET':
        username = request.GET.get('username')

        if not username:
            return JsonResponse({"error": "Username is required."}, status=400)
        
        try:
            user = User.objects.get(username=username)  # Use your custom User model if necessary
        except User.DoesNotExist:
            return JsonResponse({'detail': 'User not found.'}, status=404)

        favorites = Favorite.objects.filter(user=user).select_related('favorite_user')
        favorite_vets = [
            {
                'username': fav.favorite_user.username,
            }
            for fav in favorites
        ]

        return JsonResponse(favorite_vets, safe=False, status=200)
    
    return JsonResponse({'detail': 'Method not allowed.'}, status=405)

@csrf_exempt
def add_favorite(request):
    if request.method == 'POST':
        # Get data from the request body
        data = request.POST
        username = data.get('username')
        favorite_username = data.get('favorite_username')

        if not username or not favorite_username:
            return JsonResponse({"error": "Both 'username' and 'favorite_username' are required."}, status=400)
        
        try:
            user = User.objects.get(username=username)  # Current user
        except User.DoesNotExist:
            return JsonResponse({'detail': 'User not found.'}, status=404)
        
        try:
            favorite_user = User.objects.get(username=favorite_username)  # User to be added as favorite
        except User.DoesNotExist:
            return JsonResponse({'detail': 'Favorite user not found.'}, status=404)

        # Check if the user has already added this user as a favorite
        if Favorite.objects.filter(user=user, favorite_user=favorite_user).exists():
            return JsonResponse({'detail': 'This user is already in your favorites.'}, status=400)

        # Create the Favorite entry
        Favorite.objects.create(user=user, favorite_user=favorite_user)

        return JsonResponse({'detail': f'{favorite_username} has been added to your favorites.'}, status=201)
    
    return JsonResponse({'detail': 'Method not allowed.'}, status=405)