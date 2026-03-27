from django.urls import path
from .views import RegisterUserAPIView, CustomTokenObtainPairView, UserUpdateView, ChangePasswordView

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('update-profile/', UserUpdateView.as_view(), name='update-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='Change password')
]
