from django.urls import path
from .views import (
    signup,
    login,
    appointments,
    rate_vet,
    nearby_vets,
    predict_disease,
    deposit_coins,
    withdraw_coins,
    get_wallet_balance,
    get_coin_balance,
    favorite_vets,
    add_favorite,
    get_notifications,
    mark_notification_as_read
)

urlpatterns = [
    path('signup/', signup, name="signup"),
    path('login/', login, name="login"),
    path('appointments/', appointments, name="appointments_list"),
    path('ratings/', rate_vet, name="rate_vet"),
    path('nearby-vets/', nearby_vets, name="nearby-vets"),
    path("predict-disease/", predict_disease, name="predict-disease"),
    path("deposit-coins/", deposit_coins, name="deposit-coins"),
    path("withdraw-coins/", withdraw_coins, name="withdraw-coins"),
    path('get-wallet-balance/', get_wallet_balance, name='get-wallet-balance'),
    path('get-coin-balance/', get_coin_balance, name='get-coin-balance'),
    path('favorite-vets/', favorite_vets, name='favorite-vets'),
    path('add-favorite/', add_favorite, name='add-favorite'),
    path('get-notifications/', get_notifications, name='get-notifications'),
    path('mark-notification-as-read/', mark_notification_as_read, name='mark-notification-as-read'),
]
