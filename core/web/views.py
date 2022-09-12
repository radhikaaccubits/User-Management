from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import generic, View
from django.views.generic import UpdateView
from django import forms
from web import models
from web.forms import CreateProfileForm, CreateUserForm, RamdomPasswordChangeForm,Rolesform, SubscibersForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from .models import UserProfile, Roles
from django.contrib.auth.models import Group,Permission
from rest_framework import viewsets
from .serializers import role_serializer,userprofile_serializer


# Create your views here.

class IndexView(LoginRequiredMixin, generic.TemplateView):
    def get(self, request, *args, **kwargs):
        users = models.UserProfile.objects.all()
        role_list=models.Roles.objects.all()
        return render(request, 'users/userlist.html', {'object_list': users,'test':role_list})

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
            my_group = Group.objects.get(name=profile.role) 
            my_group.user_set.add(profile.user)
            # send credentials email
            thread = threading.Thread(target=self.send_registraion_mail, args=(user.id, username, password, email))
            thread.start()
        else:
            return render(request, 'users/create.html', {'profileform': profileform, 'userform': userform})
        messages.success(request, 'The record was saved successfully')
        return redirect('/')


class UpdateView(LoginRequiredMixin, UpdateView):
    def get(self,request, *args, **kwargs):
        post = UserProfile.objects.get(id=kwargs.get('post_id'))
        userform = CreateUserForm(instance=post.user)
        profileform = CreateProfileForm(instance=post)
        
        context={
            'profileform': profileform,
            'userform': userform,
            'post_id': post.id, }
        return render(request, 'users/update.html',context )
    
    def post(self,request,post_id):
        req = request.POST
        post =models.UserProfile.objects.get(id=post_id)
        prev_group=Group.objects.get(name=post.role) 
        profile_form = CreateProfileForm(request.POST, instance=post)
        user_form = CreateUserForm(request.POST, instance=post.user)
        if user_form.is_valid() and profile_form.is_valid():
            profile=profile_form.save(commit=False)
            user=user_form.save(commit=False)
            profile.user = user
            profile_form.save()
            user_form.save()
            prev_group.user_set.remove(profile.user)
            my_group = Group.objects.get(name=profile.role) 
            my_group.user_set.add(profile.user)
        else:
            return render(request,'users/update.html',{'profileform': profile_form,'userform': user_form,'post_id': post.id,})
        messages.success(request, 'The record was saved successfully')
        return redirect('/')


class DeleteView(LoginRequiredMixin, View):
    def post(self,request, *args, **kwargs):
        deleteid=request.POST.get('del')
        post = UserProfile.objects.get(id=deleteid)
        
        if not UserProfile.objects.filter(manager_id=post.id).values():
            
            post.user.is_active=False
            post.user.save()
            post.save()
            data = {"success":"True"}
            messages.success(request, 'The record was deleted successfully')
        else:
            data = {"success":"True"}
            messages.success(request, 'The User is reporting manager to another user')
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
class ManageRole(View):
    def get(self, request, *args, **kwargs):
        role_list=models.Roles.objects.all()
        return render(request, 'users/managerole.html', {'role_list':role_list,})

class UpdateRole(UpdateView):
    def get(self,request, *args, **kwargs):
        post = Roles.objects.get(id=kwargs.get('post_id'))
        roleform= Rolesform(instance=post)
        context={
            'roleform': roleform,
            'post_id': post.id, }
        return render(request, 'users/updaterole.html',context )
    def post(self,request,post_id):
        req = request.POST
        post =models.Roles.objects.get(id=post_id)
        update_group=Group.objects.get(name=post)
        role_form = Rolesform(request.POST, instance=post)
        if role_form.is_valid():
            new_group_name=role_form.cleaned_data['role']
            update_group.name=new_group_name
            update_group.save()
            role_form.save()
        else:
            return render(request,'users/updaterole.html',{'roleform': role_form,'post_id': post.id,})
        messages.success(request, 'The record was saved successfully')
        return redirect('/managerole/')

class ViewRoles(View):
     def get(self, request, *args, **kwargs):
        role_list=models.Roles.objects.all()
        
        return render(request, 'users/viewrole.html', {'role_list':role_list,})
class ViewUsers(View):
     def get(self, request, *args, **kwargs):
        user_list=models.UserProfile.objects.all().filter(user__is_active=True)
      
        return render(request, 'users/viewusers.html', {'user_list':user_list,})
    
class DeleteRole(View):
    def post(self,request, *args, **kwargs):
        deleteid=request.POST.get('del')
        post = Roles.objects.get(id=deleteid)
        if not post.get_children():
            role_assigned_to_user=UserProfile.objects.all().filter(role=post)
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

class CreateRole(View):
    def get(self,request):
        roleform = Rolesform(initial={'parent': 123})
        return render(request, 'users/createrole.html', {
            'roleform': roleform,})
    def post(self,request):
        roleform = Rolesform(request.POST)
        if roleform.is_valid():
            group_name=roleform.cleaned_data['role']
            Group.objects.create(name=group_name)
            roleform.save()
        else:
            return render(request,'users/createrole.html',{'roleform': roleform,})
        messages.success(request, 'The record was saved successfully')
        return redirect('/managerole/')



def load_managers(request):
        role_id = request.GET.get('roleid')
        parent_role = models.Roles.objects.filter(id=role_id).values('parent_id')

        users_with_parent_role1=models.UserProfile.objects.filter(role_id__in=parent_role,user__is_active=True).values('user_id')
        users_with_parent_role=models.User.objects.filter(id__in=users_with_parent_role1,is_active=True).values('id','first_name','last_name','username')
        return render(request, 'users/managers.html', {'users':users_with_parent_role})


class role_viewset(viewsets.ModelViewSet):
    queryset=Roles.objects.all()
    serializer_class=role_serializer

class userprofile_viewset(viewsets.ModelViewSet):
    queryset=UserProfile.objects.filter(user__is_active=True)
    serializer_class=userprofile_serializer

class Newsletter(View):
    # def post(self,request):
    #     if request.method == 'POST':
    #         form = SubscibersForm(request.POST)
    #         if form.is_valid():
    #             form.save()
    #             messages.success(request, 'Subscription Successful')
    #             return redirect('/')
    def get(self,request):
        form = SubscibersForm()
        context = {
            'form': form,
        }
        return render(request, 'users/newsletter.html', context)