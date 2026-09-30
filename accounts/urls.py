from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, StaffCreateCustomerView, CustomerListView
from .views import RequestActivationView, ActivateAccountView


urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('customers/create/', StaffCreateCustomerView.as_view(), name='customer-create'),
    path('auth/request-activation/', RequestActivationView.as_view(), name='request-activation'),
    path('auth/activate/', ActivateAccountView.as_view(), name='activate'),
    
]
