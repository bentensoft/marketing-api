from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, obj):
        if obj.profile.avatar:
            return 'https://api.yaelconsulting.com%s' % obj.profile.avatar.url
        return 'https://thecatapi.com/api/images/get?format=src&type=png'

    class Meta:
        model = User
        fields = ('id', 'username', 'avatar')


class UserIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id',)
