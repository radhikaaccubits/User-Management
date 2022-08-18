from django.shortcuts import render,redirect
from django.views import generic,View
from django.views.generic import UpdateView
from django.contrib import messages
from django.http import JsonResponse
from .models import  UserProfile,Roles
from web import models
from web.forms import CreateProfileForm,CreateUserForm,Rolesform
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
        role_form = Rolesform(request.POST, instance=post)
        if role_form.is_valid():
            role_form.save()
        else:
            return render(request,'users/updaterole.html',{'roleform': role_form,'post_id': post.id,})
        messages.success(request, 'The record was saved successfully')
        return redirect('/managerole/')

class ViewRoles(View):
     def get(self, request, *args, **kwargs):
        role_list=models.Roles.objects.all()
        return render(request, 'users/viewrole.html', {'role_list':role_list,})
    
class DeleteRole(View):
    def post(self,request, *args, **kwargs):
        deleteid=request.POST.get('del')
        post = Roles.objects.get(id=deleteid)
        if not post.get_children():
            users_del_role1=UserProfile.objects.all().filter(role=post)
            if not users_del_role1:
                post.delete()
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
            roleform.save()
        else:
            return render(request,'users/createrole.html',{'roleform': roleform,})
        messages.success(request, 'The record was saved successfully')
        return redirect('/managerole/')

class IndexView(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        data = models.UserProfile.objects.all()
        role_list=models.Roles.objects.all()
        return render(request, 'users/userlist.html', {'object_list': data,'test':role_list})
 
class CreateUser(View):
    def get(self,request):
        profileform = CreateProfileForm()
        userform = CreateUserForm()
        rolesform=Rolesform()
        return render(request, 'users/create.html', {
            'profileform': profileform,
            'userform': userform,
            'rolesform':rolesform,})
    def post(self,request):
        profileform = CreateProfileForm(request.POST)
        userform = CreateUserForm(request.POST)
        if profileform.is_valid() and userform.is_valid():
            profile=profileform.save(commit=False)
            user=userform.save()
            profile.user = user
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
        post.user.is_active=False
        post.user.save()
        post.save()
        data = {"success":"True"}
        messages.success(request, 'The record was deleted successfully')
        return JsonResponse(data)

