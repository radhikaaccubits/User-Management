import uuid
from django.contrib.auth.models import User
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView,UpdateAPIView
from .serializers import UserSerializer, ProfileSerializer
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from web.models import UserProfile
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets
from .serializers import Role_serializer, Userprofile_serializer
from django.core.exceptions import ValidationError
from django.http import Http404
from web.models import UserProfile, Roles
from rest_framework.viewsets import ViewSet

class Role_viewset(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Roles.objects.all()
    serializer_class = Role_serializer


class Userprofile_viewset(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.filter(user__is_active=True)
    serializer_class = Userprofile_serializer

class UserEndpoint(ViewSet):
    permission_classes = (IsAuthenticated,)
    
    def list(self, request):
        users  = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    def send_registraion_mail(self, user_id, username, password, email):
        subject = "User Registraion"
        template = "users/registration_email.html"
        context = {
            "id":user_id,
            "username" : username,
            "password" : password
            
        }
        message_body = render_to_string(template, context)
        send_mail(subject, message_body, settings.EMAIL_HOST_USER, [email],html_message=message_body)
    
    def create(self, request):
        user_serializer = UserSerializer(data=request.data)
        profile_serializer = ProfileSerializer(data=request.data)
        if user_serializer.is_valid(raise_exception=True) and profile_serializer.is_valid(raise_exception=True):
            user = user_serializer.save()
            user.set_password(request.data.get("password"))
            user.save()
            # create profile
            profile = profile_serializer.save(user=user)
            profile.save()
            return Response(user_serializer.data)


class UserDetailEndpoint(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    
class ChangePasswordEndpoint(ViewSet):
    permission_classes = (IsAuthenticated,)
    
    def create(self, request, pk):
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            raise ValidationError({"message":"Please provide valid user id"})
        if not user.check_password(request.data.get("old_password")):
            raise ValidationError({"message":"Please check your old password."})
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        if confirm_password == new_password:
            # update password with hash
            user.set_password(new_password)
            user.save()
            return Response({"message":"Password changed sucessfully"})
        else:
            raise ValidationError({"message":"New password and confirm password must be same."})
        
        

class PasswordResetView(ViewSet):

    def create(self, request):
        import uuid
        
        email = request.data.get("email", None)
        user = get_object_or_404(User, email=email)
        profile = get_object_or_404(UserProfile, user=user)
        password_rest_token = str(uuid.uuid4().hex) + str(uuid.uuid4().hex)
        # creating password reset token object
        profile.token = password_rest_token
        profile.token_status = True
        profile.save()
        return Response({"token": password_rest_token})


class PasswordResetConfirmView(ViewSet):
    def create(self, request):
        try:
            token = request.data.get("token")
            new_password = request.data.get("new_password")
            confirm_password = request.data.get("confirm_password")
        except KeyError:
            return Response(
                {"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(user__token=token, user__token_status=True)
            if new_password != confirm_password:
                return Response(
                    {"error": "New password and confirm password must be same"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not new_password.strip() and not confirm_password.strip():
                return Response(
                    {"error": "Password should not be empty"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # updating new password
            user.set_password(new_password)
            user.save()

            # set False password token status
            profile = UserProfile.objects.get(user=user, token=token)
            profile.token_status = False
            profile.save()
            return Response({"message": "Your password has been updated successfully"})

        except:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )
