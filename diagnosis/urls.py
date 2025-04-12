from django.urls import path
from .views import (
    signup,
    login,
    appointments,
    notifications,
    rate_vet,
    nearby_vets,
    predict_disease,
    deposit_coins,
    withdraw_coins,
    get_wallet_balance,
    get_coin_balance,
    get_upcoming_appointments,
    favorite_vets,
    add_favorite
)

urlpatterns = [
    path('signup/', signup, name="signup"),
    path('login/', login, name="login"),
    path('appointments/', appointments, name="appointments_list"),
    path('notifications/<int:user_id>/', notifications, name="user_notifications"),
    path('ratings/', rate_vet, name="rate_vet"),
    path('vets/nearby/', nearby_vets, name="nearby_vets"),
    path("predict/disease/", predict_disease, name="predict_disease"),
    path("deposit/coins/", deposit_coins, name="deposit_coins"),
    path("withdraw/coins/", withdraw_coins, name="withdraw_coins"),
    path('get-wallet-balance/', get_wallet_balance, name='get_wallet_balance'),
    path('get-coin-balance/', get_coin_balance, name='get_coin_balance'),
    path('get-upcoming-appointments/', get_upcoming_appointments, name='get-upcoming-appointments'),
    path('favorite-vets/', favorite_vets, name='favorite-vets'),
    path('add-favorite/', add_favorite, name='add-favorite'),
]
