from django import forms
from django.contrib.auth.models import User
from mptt.forms import TreeNodeChoiceField
from .models import UserProfile, Roles


def validpin(value):
    if len(str(value)) != 6:
        raise forms.ValidationError(' 6 characters is required')


def validcontact(value):
    if len(str(value)) != 10:
        raise forms.ValidationError(' 10 characters is required')


def empty(value):
    if len(str(value)) == 0:
        raise forms.ValidationError('Field cannot be empty')

def existing(value):
    allroles = Roles.objects.all().values_list('role',flat=True)
    if value in allroles:
        raise forms.ValidationError('Role already exists')


class CreateProfileForm(forms.ModelForm):
    address=forms.CharField()
    pincode=forms.IntegerField(validators=[validpin])
    contact=forms.IntegerField(validators=[validcontact])
    role = forms.ModelChoiceField(queryset=Roles.objects.all(),empty_label="Select the Role")
    manager = forms.ModelChoiceField(queryset=UserProfile.objects.none(),empty_label="Select the Manager")
    parent = TreeNodeChoiceField(queryset=UserProfile.objects.all(),empty_label="Select the Parent",level_indicator='',widget=forms.HiddenInput())
    class Meta:
        model=UserProfile
        fields=('address','pincode','contact','role','manager','parent')
       


    def __init__(self, *args, **kwargs):
        super(CreateProfileForm, self).__init__(*args, **kwargs)
        self.fields['manager'].required = False
        self.fields['parent'].required = False
        if 'role' in self.data:
            

            manager_id = self.data.get('role')
            
            parent_role = Roles.objects.filter(id=manager_id).values('parent_id')
            print(parent_role)
            print(UserProfile.objects.filter(role_id__in=parent_role).values('user__first_name'))
            print(UserProfile.objects.filter(role_id__in=parent_role).values('user_id'))
            a = UserProfile.objects.filter(role_id__in=parent_role).values('user_id')
            self.fields['manager'].queryset = User.objects.filter(id__in=a)
            
            print(User.objects.filter(id__in=a))


class CreateUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', "email")

class UserRegistraionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserRegistraionForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',"email", "password")


class RamdomPasswordChangeForm(forms.Form):
    old_password = forms.CharField(label='Old password', max_length=100, required=True, widget=forms.PasswordInput())
    new_password = forms.CharField(label='New password', max_length=100, required=True, widget=forms.PasswordInput())
    new_password_confirmation = forms.CharField(label='New password confirmation', max_length=100, required=True, widget=forms.PasswordInput())

    class Meta:
        fields = ('old_password', 'new_password', 'new_password_confirmation')
        
    def clean_new_password_confirmation(self):
        if self.cleaned_data['new_password'] != self.cleaned_data['new_password_confirmation']:
            raise forms.ValidationError("new password, confirmation must be same")
        return self.cleaned_data['new_password_confirmation'] 

class Rolesform(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=Roles.objects.all(),empty_label="Select the Parent",level_indicator='')
    role=forms.CharField(validators=[existing])

    class Meta:
        model=Roles
        fields=('role','parent',)
     
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].required = False

    def save(self, *args, **kwargs):
        Roles.objects.rebuild()
        return super(Rolesform, self).save(*args, **kwargs)

