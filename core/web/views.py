from django.shortcuts import render
from django.views import generic

from web import models
# Create your views here.

class IndexView(generic.TemplateView):

    def get(self, request, *args, **kwargs):
        data = models.UserProfile.objects.all()
        return render(request, 'users/userlist.html', {'object_list': data})