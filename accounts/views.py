from rest_framework import generics, permissions
from .models import Customer
from .serializers import RequestActivationSerializer, RegisterSerializer, StaffCreateCustomerSerializer, CustomerSerializer,  ActivateAccountSerializer
from django.core.mail import send_mail
from rest_framework.response import Response

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class IsRestaurantOrSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ('restaurant_admin', 'super_admin')
        )


class StaffCreateCustomerView(generics.CreateAPIView):
    serializer_class = StaffCreateCustomerSerializer
    permission_classes = [IsRestaurantOrSuperAdmin]


class CustomerListView(generics.ListAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsRestaurantOrSuperAdmin]
    queryset = Customer.objects.all()

class RequestActivationView(generics.GenericAPIView):
    serializer_class = RequestActivationSerializer
    permission_classes = [IsRestaurantOrSuperAdmin]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uid, token = serializer.generate_link()

        activation_link = f"http://127.0.0.1:8000/api/auth/activate/?uid={uid}&token={token}"

        send_mail(
            subject="Activate your account",
            message=f"Click here to set your password: {activation_link}",
            from_email="noreply@restaurantplatform.com",
            recipient_list=[serializer.user.email],
        )
        return Response({"detail": "Activation link sent."})


class ActivateAccountView(generics.GenericAPIView):
    serializer_class = ActivateAccountSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Account activated. You can now log in."})