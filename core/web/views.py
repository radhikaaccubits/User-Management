from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import generic, View
from django.views.generic import UpdateView
from web import models
from web.forms import CreateProfileForm, CreateUserForm

from .models import UserProfile


# Create your views here.

class IndexView(generic.TemplateView):

    def get(self, request, *args, **kwargs):
        data = models.UserProfile.objects.all()
        return render(request, 'users/userlist.html', {'object_list': data})


class CreateUser(View):

    def get(self, request, *args, **kwargs):
        profileform = CreateProfileForm()
        userform = CreateUserForm()
        return render(request, 'users/create.html', {
            'profileform': profileform,
            'userform': userform, })

    def post(self, request, *args, **kwargs):
        profileform = CreateProfileForm(request.POST)
        userform = CreateUserForm(request.POST)
        if profileform.is_valid() and userform.is_valid():
            profile = profileform.save(commit=False)
            user = userform.save()
            profile.user = user
            profile.save()
        else:
            return render(request, 'users/create.html', {'profileform': profileform, 'userform': userform})
        messages.success(request, 'The record was saved successfully')
        return redirect('/')


class UpdateView(UpdateView):

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


class DeleteView(View):

    def post(self, request, *args, **kwargs):
        delete_id = request.POST.get('del')
        post = UserProfile.objects.get(id=delete_id)
        post.user.is_active = False
        post.user.save()
        post.save()
        data = {"success": "True"}
        messages.success(request, 'The record was deleted successfully')
        return JsonResponse(data)
