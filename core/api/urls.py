from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path, include
from api.router import router
from .auth import UserEndpoint, UserDetailEndpoint, ChangePasswordEndpoint, PasswordResetView,PasswordResetConfirmView

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="User Management API",
      default_version='v1',
      description="Manage all the db users",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="gurrappa@accubits.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
   
)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', UserEndpoint.as_view(), name='users'),
    path('users/<int:pk>', UserDetailEndpoint.as_view(), name='users_details'),
    path('users/<int:pk>/change-password/', ChangePasswordEndpoint.as_view(), name='change_password'),
    path('password-reset/', PasswordResetView.as_view(), name='api_password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='api_password_reset_confirm'),
    # docs api
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
