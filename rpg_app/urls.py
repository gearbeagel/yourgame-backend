from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CharacterViewSet, SettingViewSet, PlotViewSet, StoryViewSet, login_view, logout_view, csrf, \
    register_view, ChatLogViewSet

router = DefaultRouter()
router.register(r'characters', CharacterViewSet)
router.register(r'settings', SettingViewSet)
router.register(r'plots', PlotViewSet)
router.register(r'stories', StoryViewSet)
router.register(r'chatlogs', ChatLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/csrf/', csrf, name='csrf'),
    path('auth/register/', register_view, name='register'),
]
