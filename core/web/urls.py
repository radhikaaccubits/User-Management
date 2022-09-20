from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('create/', views.CreateUser.as_view(), name='create'),
    path('delete/', views.DeleteView.as_view(), name='delete'),
    path('update/<int:post_id>', views.UpdateView.as_view(), name='update'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('createrole/', views.CreateRole.as_view(), name='createrole'),
    path('viewroles/', views.ViewRoles.as_view(), name='viewrole'),
    path('viewusers/', views.ViewUsers.as_view(), name='viewuser'),
    path('updaterole/<int:post_id>', views.UpdateRole.as_view(), name='updaterole'),
    path('deleterole/', views.DeleteRole.as_view(), name='delrole'),
    path('managerole/', views.ManageRole.as_view(), name='managerole'),
    path('ajax/load-managers/', views.load_managers, name='ajax_load_managers'),
    # password-change
    path('password-change/',
         auth_views.PasswordChangeView.as_view(template_name='authentication/password_change.html'),
         name='password_change'
         ),
    path('password-change-done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='authentication/password_change_done.html'),
         name='password_change_done'
         ),
    # random password change
    path("users/<int:pk>/random-password-change/", views.RandomPasswordChangeView.as_view(),
         name="random_password_change"),

    # password-reset-paths
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='authentication/password_reset.html'),
         name='password_reset'
         ),
    path('password-reset-done/',
         auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_done.html'),
         name='password_reset_done'
         ),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='authentication/password_reset_confirm.html'),
         name='password_reset_confirm'
         ),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_complete.html'),
         name='password_reset_complete'
         ),
]
