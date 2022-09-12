from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path
from .auth import UserEndpoint, UserDetailEndpoint, ChangePasswordEndpoint, PasswordResetView,PasswordResetConfirmView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', UserEndpoint.as_view(), name='users'),
    path('users/<int:pk>', UserDetailEndpoint.as_view(), name='users_details'),
    path('users/<int:pk>/change-password/', ChangePasswordEndpoint.as_view(), name='change_password'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
]