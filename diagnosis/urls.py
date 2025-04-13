from django.urls import path
from .views import (
    signup,
    vet_login,
    farmer_login,
    appointments,
    nearby_vets,
    predict_disease,
    deposit_coins,
    withdraw_coins,
    get_wallet_balance,
    get_coin_balance,
    favorite_vets,
    add_favorite,
    get_notifications,
    mark_notification_as_read,
    update_profile
)

urlpatterns = [
    path('signup/', signup, name="signup"),
    path('vet-login/', vet_login, name="vet-login"),
    path('farmer-login/', farmer_login, name="farmer-login"),
    path('update-profile/', update_profile, name="update-profile"),
    path('appointments/', appointments, name="appointments"),
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
