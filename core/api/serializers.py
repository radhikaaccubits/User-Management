from django.contrib.auth.models import User
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from web.models import UserProfile, Roles

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "username", "email")


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ("user", "token", "token_status")


class Roleserializer(serializers.ModelSerializer):
    def validate(self, value):
        roles = Roles.objects.filter(role=value['role'])
        if roles:
            raise serializers.ValidationError("Role already exists")
        else:
            return value

    class Meta:
        model = Roles
        fields = ('id', 'role', 'parent')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['parent'] = Roleserializer(instance.parent).data['role']
        return rep



class Userprofileserializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    user = UserSerializer()
    # choices=UserProfile.objects.all()
    # manager=serializers.ChoiceField(choices=choices)
    # role=role_serializer(read_only=True)
    def validate_pincode(self, value):
        if len(str(value)) != 6:
            raise serializers.ValidationError(' 6 characters is required')
        else:
            return value

    def validate_contact(self, value):
        if len(str(value)) != 10:
            raise serializers.ValidationError(' 10 characters is required')
        else:
            return value

    def validate_manager(self, value):

        role_id = self.initial_data.get('role')
        parent_role = Roles.objects.filter(id=role_id).values('parent_id')

        userprofile_with_parent_role = UserProfile.objects.filter(role_id__in=parent_role, user__is_active=True).values(
            'user_id')
        users_with_parent_role = User.objects.filter(id__in=userprofile_with_parent_role, is_active=True).values('id',
                                                                                                            'first_name',
                                                                                                            'last_name',
                                                                                                            'username')
        managers = []
        for i in users_with_parent_role:
            managers.append(i['username'])

        error = {"Please select from: ": managers}
        
        if str(value) not in managers:
            raise serializers.ValidationError(error)
        else:
            return value

    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'address', 'pincode', 'contact', 'role', 'manager')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['role'] = Roleserializer(instance.role).data['role']
        return rep
