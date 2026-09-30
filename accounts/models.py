from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        RESTAURANT_ADMIN = "restaurant_admin", "Restaurant Admin"
        CUSTOMER = "customer", "Customer"
    role=models.CharField(max_length=20, choices=Role.choices)

class Customer(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone=models.CharField(max_length=20, blank=True)
    address=models.TextField(blank=True, max_length=500)
    dietary_preferences=models.CharField(max_length=100, blank=True)
    created_by_staff=models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name() or self.user.username