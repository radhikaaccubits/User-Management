from django.contrib.auth.models import User
from web.models import UserProfile

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id","first_name", "last_name", "username", "email")

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ("user","token","token_status")