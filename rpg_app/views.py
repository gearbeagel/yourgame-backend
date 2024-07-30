import json
import os

import openai
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt, csrf_protect
from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import Character, Setting, Plot, Story, ChatLog
from .serializers import CharacterSerializer, SettingSerializer, PlotSerializer, StorySerializer, ChatLogSerializer

openai.api_key = os.environ['openai_api_key']


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=True, methods=['get'])
    def chat_logs(self, request, pk=None):
        story = get_object_or_404(Story, id=pk, user=request.user)
        chat_logs = story.chat_logs.all().order_by('timestamp')
        serializer = ChatLogSerializer(chat_logs, many=True)
        return Response({'chat_logs': serializer.data})


class CharacterViewSet(viewsets.ModelViewSet):
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(story__user=self.request.user)


class SettingViewSet(viewsets.ModelViewSet):
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(story__user=self.request.user)


class PlotViewSet(viewsets.ModelViewSet):
    queryset = Plot.objects.all()
    serializer_class = PlotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(story__user=self.request.user)


class ChatLogViewSet(viewsets.ModelViewSet):
    queryset = ChatLog.objects.all()
    serializer_class = ChatLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.filter(story__user=self.request.user).order_by('-timestamp')
        print(f"Debug: Fetched queryset with {queryset.count()} entries.")
        return queryset

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        message_data = request.data.get('message_data')

        print(f"Debug: Received PATCH request with messages={message_data}")

        if not message_data:
            print("Debug: Messages are missing.")
            return JsonResponse({'error': 'Messages are required'}, status=400)

        if isinstance(instance.message_data, dict):
            instance.message_data.update(message_data)
        else:
            instance.message_data = message_data

        instance.save()

        serializer = self.get_serializer(instance)
        print("Debug: Updated chat log and saved changes.")
        return Response(serializer.data)


@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({"message": "CSRF cookie set"})


@csrf_exempt
def register_view(request):
    if request.method != 'POST':
        return JsonResponse({"message": "Invalid request method."}, status=400)
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return JsonResponse({"message": "Make sure to fill in all of the fields."}, status=400)
    try:
        user = User.objects.create_user(username, email, password)
        user.save()
        login(request, user)
        return JsonResponse({"message": "User created successfully."})
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=400)


@csrf_protect
def login_view(request):
    if request.method != 'POST':
        return JsonResponse({"message": "Invalid request method."}, status=400)
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({"message": "Login successful"})
    else:
        return JsonResponse({"message": "Invalid credentials"}, status=400)


def logout_view(request):
    logout(request)
    return JsonResponse({"message": "Logout successful"})
