from random import choices
from wsgiref import validate
from wsgiref.validate import validator
from xml.dom import ValidationErr
from rest_framework import serializers
from .models import Roles,UserProfile
from django.contrib.auth.models import User
from drf_writable_nested import WritableNestedModelSerializer

class role_serializer(serializers.ModelSerializer):
    def validate(self,value):
        a=Roles.objects.filter(role=value['role'])
        if a:
            raise serializers.ValidationError("Role already exists")
        else:
            return value
 
        
    class Meta:
        model=Roles
        fields=('id','role','parent')
        
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['parent'] = role_serializer(instance.parent).data['role']
        return rep
   




class user1_serializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=('first_name','last_name','username')

class userprofile_serializer(WritableNestedModelSerializer,serializers.ModelSerializer):
    user=user1_serializer()
    # choices=UserProfile.objects.all()
    
    # manager=serializers.ChoiceField(choices=choices)
    #role=role_serializer(read_only=True)
    def validate_pincode(self,value):
        if len(str(value)) != 6:
            raise serializers.ValidationError(' 6 characters is required')
        else:
            return value


    def validate_contact(self,value):
        if len(str(value)) != 10:
            raise serializers.ValidationError(' 10 characters is required')
        else:
            return value
    class Meta:
        model=UserProfile

        fields=('id','user','address','pincode','contact','role','manager')
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        

        rep['role'] = role_serializer(instance.role).data['role']
        return rep
        
    


        