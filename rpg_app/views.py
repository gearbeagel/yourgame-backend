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

    def create(self, request, *args, **kwargs):
        story_id = request.data.get('story')
        user_message = request.data.get('content')

        print(f"Debug: Received POST request with story_id={story_id} and user_message={user_message}")

        if not story_id or not user_message:
            print("Debug: Story ID or content is missing.")
            return JsonResponse({'error': 'Story ID and content are required'}, status=400)

        try:
            story = Story.objects.get(id=story_id, user=request.user)
            print(f"Debug: Found story with id={story_id}.")
        except Story.DoesNotExist:
            print(f"Debug: Story with id={story_id} not found.")
            return JsonResponse({'error': 'Story not found'}, status=404)

        plot = ' '.join(story.plots.values_list('summary', flat=True))
        characters = ' '.join(story.characters.values_list('name', flat=True))
        settings = ' '.join(story.settings.values_list('description', flat=True))

        prompt = f"Plot: {plot}\nCharacters: {characters}\nSettings: {settings}\n\nUser Message: {user_message}\n\nResponse:"

        print(f"Debug: Generated prompt for OpenAI: {prompt}")

        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=150
            )
            ai_message = response.choices[0].text.strip()
            print(f"Debug: Received AI response: {ai_message}")
        except Exception as e:
            print(f"Debug: OpenAI API Error: {str(e)}")
            return JsonResponse({'error': f'OpenAI API Error: {str(e)}'}, status=500)

        # Create user message and AI response chat logs
        ChatLog.objects.create(
            story=story,
            message_data=[
                {
                    'timestamp': timezone.now().isoformat(),
                    'sender': 'user',
                    'content': user_message
                },
                {
                    'timestamp': timezone.now().isoformat(),
                    'sender': 'ai',
                    'content': ai_message
                }
            ]
        )

        print("Debug: Created chat logs for user message and AI response.")

        return JsonResponse({
            'user_message': user_message,
            'ai_message': ai_message,
            'message_data': [
                {
                    'timestamp': timezone.now().isoformat(),
                    'sender': 'user',
                    'content': user_message
                },
                {
                    'timestamp': timezone.now().isoformat(),
                    'sender': 'ai',
                    'content': ai_message
                }
            ]
        })

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        message_data = request.data.get('message_data')

        print(f"Debug: Received PATCH request with messages={message_data}")

        if not message_data:
            print("Debug: Messages are missing.")
            return JsonResponse({'error': 'Messages are required'}, status=400)

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
