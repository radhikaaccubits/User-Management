from http.client import HTTPResponse
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import generic, View
from django.views.generic import UpdateView
from django import forms
from web import models
from web.forms import CreateProfileForm, CreateUserForm, RamdomPasswordChangeForm,Rolesform
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from .models import UserProfile, Roles
from django.contrib.auth.models import Group,Permission
from rest_framework import viewsets
from django.core.exceptions import ValidationError
from django.http import Http404


# Create your views here.

class IndexView(LoginRequiredMixin, generic.TemplateView):
    def get(self, request, *args, **kwargs):
        
        users = UserProfile.objects.all()
        role_list=Roles.objects.all()
        return render(request, 'users/userlist.html', {'object_list': users,'test':role_list})

class UserLoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'Invalid Username or Password')
            return render(request, 'authentication/login.html')

class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect("index")
        
        
class CreateUser(LoginRequiredMixin, View):
    def send_registraion_mail(self, user_id, username, password, email,request):
        
        subject = "User Registraion"
        template = "authentication/registration_email.html"
        context = {
            "id":user_id,
            "username" : username,
            "password" : password,
            "domain": request.build_absolute_uri('/')[:-1],
            
            
            
        }
        message_body = render_to_string(template, context)
        send_mail(subject, message_body, settings.EMAIL_HOST_USER, [email],html_message=message_body)
        
    def get(self, request, *args, **kwargs):
        profileform = CreateProfileForm()
        userform = CreateUserForm()
        return render(request, 'users/create.html', {
            'profileform': profileform,
            'userform': userform,
            })
        
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
            user = userform.save(commit=False)
            user.set_password(password)
            user.save()
            profile.user = user
            test=profile.manager_id
        
            #profile.parent_id=test
            profile.save()
            # my_group = Group.objects.get(name=profile.role) 
            # my_group.user_set.add(profile.user)
            # send credentials email
            thread = threading.Thread(target=self.send_registraion_mail, args=(user.id, username, password, email,request))
            thread.start()
        else:
            return render(request, 'users/create.html', {'profileform': profileform, 'userform': userform})
        messages.success(request, 'The record was saved successfully')
        return redirect('/')


class UpdateView(LoginRequiredMixin, UpdateView):
    def get(self,request, *args, **kwargs):
        try:
            post = UserProfile.objects.get(id=kwargs.get('post_id'))
        except UserProfile.DoesNotExist:
            raise Http404
        userform = CreateUserForm(instance=post.user)
        profileform = CreateProfileForm(instance=post)
        
        context={
            'profileform': profileform,
            'userform': userform,
            'post_id': post.id, }
        return render(request, 'users/update.html',context )
    
    def post(self,request,post_id):
        req = request.POST
        try:
            post =UserProfile.objects.get(id=post_id)
        except UserProfile.DoesNotExist:
            raise Http404
        # prev_group=Group.objects.get(name=post.role) 
        profile_form = CreateProfileForm(request.POST, instance=post)
        user_form = CreateUserForm(request.POST, instance=post.user)
        if user_form.is_valid() and profile_form.is_valid():
            profile=profile_form.save(commit=False)
            user=user_form.save(commit=False)
            profile.user = user
            profile_form.save()
            user_form.save()
            # prev_group.user_set.remove(profile.user)
            # my_group = Group.objects.get(name=profile.role) 
            # my_group.user_set.add(profile.user)
        else:
            return render(request,'users/update.html',{'profileform': profile_form,'userform': user_form,'post_id': post.id,})
        messages.success(request, 'The record was saved successfully')
        return redirect('/')


class DeleteView(LoginRequiredMixin, View):
    def post(self,request, *args, **kwargs):
        deleteid=request.POST.get('del')
        try:
            post = UserProfile.objects.get(id=deleteid)
        except UserProfile.DoesNotExist:
            raise Http404
        current_user_id=UserProfile.objects.filter(id=deleteid).values('user_id')
        
        users_below=UserProfile.objects.filter(manager_id__in=current_user_id).exists()
        if not users_below:
            
            post.user.is_active=False
            post.user.save()
            post.save()
            data = {"success":"True"}
            
        else:
            data = {"success":"True"}
            messages.success(request, 'The User is reporting manager to another user')
        return JsonResponse(data)


class RandomPasswordChangeView(View):
    def get(self, request, pk):
        form = RamdomPasswordChangeForm()
        return render(request, "authentication/random_password_change.html",{"form":form})
    
    def post(self, request, pk):
        form = RamdomPasswordChangeForm(request.POST)
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        user = User.objects.filter(id=pk).first()
        if form.is_valid():
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                return render(request, "authentication/random_password_change_done.html")
            else:
                form.add_error("old_password", "wrong password")
                return render(request, "authentication/random_password_change.html",{"form":form})
        else:
            return render(request, "authentication/random_password_change.html",{"form":form})
class ManageRole(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        role_list=Roles.objects.all()
        return render(request, 'roles/managerole.html', {'role_list':role_list,})

class UpdateRole(LoginRequiredMixin,View):
    def get(self,request, *args, **kwargs):
        try:
            post = Roles.objects.get(id=kwargs.get('post_id'))
        except Roles.DoesNotExist:
            raise Http404
        roleform= Rolesform(instance=post)
        context={
            'roleform': roleform,
            'post_id': post.id, }
        return render(request, 'roles/updaterole.html',context )
    def post(self,request,post_id):
        req = request.POST
        try:
            post =Roles.objects.get(id=post_id)
        except Roles.DoesNotExist:
            raise Http404
        # update_group=Group.objects.get(name=post)
        role_form = Rolesform(request.POST, instance=post)
        
        
        if role_form.is_valid():
            # new_group_name=role_form.cleaned_data['role']
            # update_group.name=new_group_name
            # update_group.save()
            role_form.save()
        else:
            return render(request,'roles/updaterole.html',{'roleform': role_form,'post_id': post.id,})
        messages.success(request, 'The record was saved successfully')
        return redirect('/managerole/')

class ViewRoles(LoginRequiredMixin,View):
     def get(self, request, *args, **kwargs):
        role_list=Roles.objects.filter(is_active=True)
        
        return render(request, 'roles/viewrole.html', {'role_list':role_list,})
class ViewUsers(LoginRequiredMixin,View):
     def get(self, request, *args, **kwargs):
        user_list=UserProfile.objects.all().filter(user__is_active=True)
      
        return render(request, 'users/viewusers.html', {'user_list':user_list,})
    
class DeleteRole(LoginRequiredMixin,View):
    def post(self,request, *args, **kwargs):
        deleteid=request.POST.get('del')
        try:
            post = Roles.objects.get(id=deleteid)
        except Roles.DoesNotExist:
            raise Http404
        if not post.get_children():
            role_assigned_to_user=UserProfile.objects.filter(role=post).exists()
            
            if not role_assigned_to_user:
                post.is_active=False
                post.save()
                messages.success(request, 'The record was deleted successfully')
            else:
                data={"Error":"Role Assigned"}
                messages.success(request, 'Role is already assigned to user, Cannot delete it') 
        else:
            data={"Error":"Children exists"}
            messages.success(request, 'Cannot delete role because it has children')
        data = {"success":"True"}
        return JsonResponse(data)

class CreateRole(LoginRequiredMixin,View):
    def get(self,request):
        roleform = Rolesform(initial={'parent': 123})
        return render(request, 'roles/createrole.html', {
            'roleform': roleform,})
    def post(self,request):
        roleform = Rolesform(request.POST)
        if roleform.is_valid():
            group_name=roleform.cleaned_data['role']
            Group.objects.create(name=group_name)
            roleform.save()
        else:
            return render(request,'roles/createrole.html',{'roleform': roleform,})
        messages.success(request, 'The record was saved successfully')
        return redirect('/managerole/')



def load_managers(request):
        role_id = request.GET.get('roleid')
        parent_role = Roles.objects.filter(id=role_id).values('parent_id')

        users_with_parent_role1=UserProfile.objects.filter(role_id__in=parent_role,user__is_active=True).values('user_id')
        users_with_parent_role=User.objects.filter(id__in=users_with_parent_role1,is_active=True).values('id','first_name','last_name','username')
        return render(request, 'users/managers.html', {'users':users_with_parent_role})







