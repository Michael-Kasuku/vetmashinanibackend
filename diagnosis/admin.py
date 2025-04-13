from django.contrib import admin
from diagnosis.models import User, CertifiedVet, VeterinarianProfile, FarmerProfile, Appointment, Notification, Favorite, Rating, CoinReward, PlatformCoin

# List of all the models you want to register
models = [User,CertifiedVet, VeterinarianProfile, FarmerProfile, Appointment, Notification, Favorite, Rating, CoinReward,PlatformCoin]

# Loop through the models and register them in the admin site
for model in models:
    admin.site.register(model)
