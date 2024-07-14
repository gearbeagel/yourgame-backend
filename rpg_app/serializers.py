from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Character, Setting, Plot, Story

class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = '__all__'


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = '__all__'


class PlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plot
        fields = '__all__'


class StorySerializer(serializers.ModelSerializer):
    characters = CharacterSerializer(many=True, read_only=True)
    settings = SettingSerializer(many=True, read_only=True)
    plots = PlotSerializer(many=True, read_only=True)

    class Meta:
        model = Story
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        user = User.objects.update(**validated_data)
        return user

