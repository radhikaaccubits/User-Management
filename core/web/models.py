from django.db import models
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.

class UserProfile(models.Model):
    user=models.OneToOneField(User,related_name='user', on_delete=models.CASCADE)
    address=models.CharField(max_length=100)
    pincode=models.CharField(max_length=6)
    contact=models.CharField(max_length=15)
    role=models.CharField(max_length=20,default="Manager")
    
class Roles(MPTTModel):
    role=models.CharField(max_length=15)
    parent = TreeForeignKey('self', on_delete=models.CASCADE,null=True, blank=True, related_name='children')
    def __str__(self):
        return self.role
    
