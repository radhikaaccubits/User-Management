from django import forms
from .models import UserProfile,Roles
from django.contrib.auth.models import User
from mptt.forms import TreeNodeChoiceField

def validpin(value):
    if len(str(value)) != 6:
        raise forms.ValidationError(' 6 characters is required')

def validcontact(value):
    if len(str(value)) != 10:
        raise forms.ValidationError(' 10 characters is required')

def empty(value):
    if len(str(value))==0:
        raise forms.ValidationError('Field cannot be empty')

def existing(value):
    a = Roles.objects.all().values_list('role',flat=True)
    if value in a:
        raise forms.ValidationError('Role already exists')
    
   
class CreateProfileForm(forms.ModelForm):
    address=forms.CharField()
    pincode=forms.IntegerField(validators=[validpin])
    contact=forms.IntegerField(validators=[validcontact])
    role = forms.ModelChoiceField(queryset=Roles.objects.all(),empty_label="Select the Role")

    class Meta:
        model=UserProfile
        fields=('address','pincode','contact','role')

class CreateUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        
    class Meta:
        model=User
        fields=('first_name','last_name','username')

class Rolesform(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=Roles.objects.all(),empty_label="Select the Parent",level_indicator='')
    role=forms.CharField(validators=[existing])

    class Meta:
        model=Roles
        fields=('role','parent',)
     
    def save(self, *args, **kwargs):
        Roles.objects.rebuild()
        return super(Rolesform, self).save(*args, **kwargs)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].required = False
        