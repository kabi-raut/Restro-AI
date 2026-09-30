from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Customer
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator

User=get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,min_length=8)
    phone= serializers.CharField(write_only=True, required=False, allow_blank=True)
    address=serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model=User
        fields=['id','username','email','password','phone','address']

    def create(self, validated_data):
        phone = validated_data.pop('phone', '')
        address = validated_data.pop('address', '')
        password = validated_data.pop('password')

        user = User(**validated_data, role=User.Role.CUSTOMER)
        user.set_password(password)
        user.save()

        Customer.objects.create(
            user=user, phone=phone, address=address, created_by_staff=False
        )
        return user

class StaffCreateCustomerSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    address = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'address']

    def create(self, validated_data):
        phone = validated_data.pop('phone', '')
        address = validated_data.pop('address', '')

        user = User(**validated_data, role=User.Role.CUSTOMER)
        user.set_unusable_password()
        user.save()

        Customer.objects.create(
            user=user, phone=phone, address=address, created_by_staff=True
        )
        return user

class CustomerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    has_claimed_account = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ['id', 'username', 'email', 'phone', 'address', 'dietary_preferences',
                  'created_by_staff', 'has_claimed_account']

    def get_has_claimed_account(self, obj):
        return obj.user.has_usable_password()

account_activation_token = PasswordResetTokenGenerator()


class RequestActivationSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate_username(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this username.")
        if user.has_usable_password():
            raise serializers.ValidationError("This account is already activated.")
        self.user = user
        return value

    def generate_link(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_activation_token.make_token(self.user)
        return uid, token


class ActivateAccountSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uid']))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError("Invalid activation link.")

        if not account_activation_token.check_token(user, data['token']):
            raise serializers.ValidationError("This activation link is invalid or has expired.")

        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['password'])
        user.save()
        return user