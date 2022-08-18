from django.urls import  path
from . import views

urlpatterns  = [
    path('', views.IndexView.as_view(), name='index'),
    path('create/', views.CreateUser.as_view(), name='create'),
    path('delete/', views.DeleteView.as_view(), name='delete'),
    path('createrole/', views.CreateRole.as_view(), name='role'),
    path('viewroles/', views.ViewRoles.as_view(), name='viewrole'),
    path('updaterole/<int:post_id>', views.UpdateRole.as_view(), name='updaterole'),
    path('deleterole/', views.DeleteRole.as_view(), name='delrole'),
    path('managerole/', views.ManageRole.as_view(), name='managerole'),
    path('update/<int:post_id>', views.UpdateView.as_view(), name='update'),
    
]