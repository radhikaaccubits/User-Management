from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import generic, View
from django.views.generic import UpdateView
from django import forms
from web import models
from web.forms import CreateProfileForm, CreateUserForm, RamdomPasswordChangeForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from .models import UserProfile


# Create your views here.

class IndexView(LoginRequiredMixin, generic.TemplateView):
    
    def get(self, request, *args, **kwargs):
        data = models.UserProfile.objects.all()
        return render(request, 'users/userlist.html', {'object_list': data})

class UserLoginView(View):
    def get(self, request):
        return render(request, 'users/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'Invalid Username or Password')
            return render(request, 'users/login.html')

class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect("index")
        
        
class CreateUser(LoginRequiredMixin, View):
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
        
    def get(self, request, *args, **kwargs):
        profileform = CreateProfileForm()
        userform = CreateUserForm()
        return render(request, 'users/create.html', {
            'profileform': profileform,
            'userform': userform, })

    def post(self, request, *args, **kwargs):
        import uuid
        import threading
        
        profileform = CreateProfileForm(request.POST)
        userform = CreateUserForm(request.POST)
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = uuid.uuid4().hex[:8]
        if profileform.is_valid() and userform.is_valid():
            profile = profileform.save(commit=False)
            user = userform.save()
            user.set_password(password)
            user.save()
            profile.user = user
            profile.save()
            # send credentials email
            thread = threading.Thread(target=self.send_registraion_mail, args=(user.id, username, password, email))
            thread.start()
        else:
            return render(request, 'users/create.html', {'profileform': profileform, 'userform': userform})
        messages.success(request, 'The record was saved successfully')
        return redirect('/')


class UpdateView(LoginRequiredMixin, UpdateView):

    def get(self, request, *args, **kwargs):
        post = UserProfile.objects.get(id=kwargs.get('post_id'))
        userform = CreateUserForm(instance=post.user)
        profileform = CreateProfileForm(instance=post)
        context = {
            'profileform': profileform,
            'userform': userform,
            'post_id': post.id, }
        return render(request, 'users/update.html', context)

    def post(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        post = models.UserProfile.objects.get(id=post_id)
        profile_form = CreateProfileForm(request.POST, instance=post)
        user_form = CreateUserForm(request.POST, instance=post.user)
        if user_form.is_valid() and profile_form.is_valid():
            profile_form.save()
            user_form.save()
        else:
            return render(request, 'users/update.html',
                          {'profileform': profile_form,
                           'userform': user_form,
                           'post_id': post.id, })
        messages.success(request, 'The record was saved successfully')
        return redirect('/')


class DeleteView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        delete_id = request.POST.get('del')
        post = UserProfile.objects.get(id=delete_id)
        post.user.is_active = False
        post.user.save()
        post.save()
        data = {"success": "True"}
        messages.success(request, 'The record was deleted successfully')
        return JsonResponse(data)


class RandomPasswordChangeView(View):
    def get(self, request, pk):
        form = RamdomPasswordChangeForm()
        return render(request, "users/random_password_change.html",{"form":form})
    
    def post(self, request, pk):
        form = RamdomPasswordChangeForm(request.POST)
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        user = User.objects.filter(id=pk).first()
        if form.is_valid():
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                return render(request, "users/random_password_change_done.html")
            else:
                form.add_error("old_password", "wrong password")
                return render(request, "users/random_password_change.html",{"form":form})
        else:
            return render(request, "users/random_password_change.html",{"form":form})