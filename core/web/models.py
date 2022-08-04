from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):  
    user=models.OneToOneField(User,related_name='user', on_delete=models.CASCADE)
    address=models.CharField(max_length=100)
    pincode=models.CharField(max_length=6)
    contact=models.CharField(max_length=15)
    
    