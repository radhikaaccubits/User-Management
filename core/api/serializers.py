from django.contrib.auth.models import User
from web.models import UserProfile, Roles

from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id","first_name", "last_name", "username", "email")

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ("user","token","token_status")
