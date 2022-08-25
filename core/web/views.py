from django.shortcuts import render,redirect
from django.views import generic,View
from django.views.generic import UpdateView
from django.contrib import messages
from django.http import JsonResponse
from .models import  UserProfile,Roles
from web import models
from web.forms import CreateProfileForm,CreateUserForm,Rolesform
from django.contrib.auth.models import Group,Permission

# Create your views here.

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

class IndexView(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        users = models.UserProfile.objects.all()
        role_list=models.Roles.objects.all()
        return render(request, 'users/userlist.html', {'object_list': users,'test':role_list})


def load_managers(request):
    role_id = request.GET.get('roleid')
    parent_role = models.Roles.objects.filter(id=role_id).values('parent_id')

    users_with_parent_role=models.UserProfile.objects.filter(role_id__in=parent_role,user__is_active=True).values('id', 'user__first_name', 'user__last_name',)
    return render(request, 'users/managers.html', {'users':users_with_parent_role})

class CreateUser(View):
    
    def get(self,request):
        
        profileform = CreateProfileForm()
        userform = CreateUserForm()
        return render(request, 'users/create.html', {
            'profileform': profileform,
            'userform': userform,
            })
    def post(self,request):
        profileform = CreateProfileForm(request.POST)
        userform = CreateUserForm(request.POST)
        if profileform.is_valid() and userform.is_valid():
            profile=profileform.save(commit=False)
            user=userform.save()
            profile.user = user
            test=profile.manager_id
            profile.parent_id=test
            profile.save()
        else:
            return render(request,'users/create.html',{'profileform': profileform,'userform': userform})
        messages.success(request, 'The record was saved successfully')
        return redirect('/')
        
class UpdateView(UpdateView):
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
        profile_form = CreateProfileForm(request.POST, instance=post)
        user_form = CreateUserForm(request.POST, instance=post.user)
        if user_form.is_valid() and profile_form.is_valid():
            
            profile_form.save()
            user_form.save()
        else:
            return render(request,'users/update.html',{'profileform': profile_form,'userform': user_form,'post_id': post.id,})
        messages.success(request, 'The record was saved successfully')
        return redirect('/')

class DeleteView(View):
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

