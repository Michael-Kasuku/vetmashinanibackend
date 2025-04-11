from django.urls import path
from .views import (
    signup,
    login,
    appointments,
    notifications,
    favorites,
    rate_vet,
    nearby_vets,
    predict_disease,
    deposit_coins,
    withdraw_coins
)

urlpatterns = [
    path('signup/', signup, name="signup"),
    path('login/', login, name="login"),
    path('appointments/', appointments, name="appointments_list"),
    path('notifications/<int:user_id>/', notifications, name="user_notifications"),
    path('favorites/', favorites, name="create_favorite"),
    path('favorites/<int:user_id>/', favorites, name="list_favorites"),
    path('ratings/', rate_vet, name="rate_vet"),
    path('vets/nearby/', nearby_vets, name="nearby_vets"),
    path("predict/disease/", predict_disease, name="predict_disease"),
    path("deposit/coins/", deposit_coins, name="deposit_coins"),
    path("withdraw/coins/", withdraw_coins, name="withdraw_coins"),
]
