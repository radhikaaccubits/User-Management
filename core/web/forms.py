from django import forms
from django.contrib.auth.models import User

from .models import UserProfile


def validpin(value):
    if len(str(value)) != 6:
        raise forms.ValidationError(' 6 characters is required')


def validcontact(value):
    if len(str(value)) != 10:
        raise forms.ValidationError(' 10 characters is required')


def empty(value):
    if len(str(value)) == 0:
        raise forms.ValidationError('Field cannot be empty')


class CreateProfileForm(forms.ModelForm):
    address = forms.CharField()
    pincode = forms.IntegerField(validators=[validpin])
    contact = forms.IntegerField(validators=[validcontact])

    class Meta:
        model = UserProfile
        fields = ('address', 'pincode', 'contact')


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

