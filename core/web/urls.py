from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('create/', views.CreateUser.as_view(), name='create'),
    path('delete/', views.DeleteView.as_view(), name='delete'),
    path('update/<int:post_id>', views.UpdateView.as_view(), name='update'),

]
