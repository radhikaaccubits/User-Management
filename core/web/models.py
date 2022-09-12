from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.
class Roles(MPTTModel):
    role=models.CharField(max_length=15)
    parent = TreeForeignKey('self', on_delete=models.CASCADE,null=True, blank=True, related_name='children')
    is_active=models.BooleanField(default=True)
    def __str__(self):
        return self.role
class UserProfile(MPTTModel):
    user=models.OneToOneField(User,related_name='user', on_delete=models.CASCADE)
    address=models.CharField(max_length=100)
    pincode=models.CharField(max_length=6)
    contact=models.CharField(max_length=15)
    role=models.ForeignKey(Roles, on_delete=models.CASCADE)
    manager=models.ForeignKey(User,related_name='manager', on_delete=models.CASCADE,null=True)
    parent=TreeForeignKey('self', on_delete=models.CASCADE,null=True, blank=True, related_name='children')
    token = models.CharField(max_length=256, null=True, blank=True)
    token_status = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        if self.manager_id:
            a=UserProfile.objects.values('id').get(user_id=self.manager_id)['id']
        
            print(a)
            self.parent_id= a

        super(UserProfile, self).save(*args, **kwargs)
    # def __str__(self):
    #     return self.user.first_name
    
    
    


