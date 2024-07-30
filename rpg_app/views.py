import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt, csrf_protect
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Character, Setting, Plot, Story
from .serializers import CharacterSerializer, SettingSerializer, PlotSerializer, StorySerializer


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


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
