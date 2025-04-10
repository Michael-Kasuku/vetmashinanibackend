from django.contrib import admin
from diagnosis.models import User, VeterinarianProfile, FarmerProfile, Appointment, Notification, Favorite, Rating

# List of all the models you want to register
models = [User, VeterinarianProfile, FarmerProfile, Appointment, Notification, Favorite, Rating]

# Loop through the models and register them in the admin site
for model in models:
    admin.site.register(model)
