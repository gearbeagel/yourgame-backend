from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CharacterViewSet, SettingViewSet, PlotViewSet, StoryViewSet

router = DefaultRouter()
router.register(r'characters', CharacterViewSet)
router.register(r'settings', SettingViewSet)
router.register(r'plots', PlotViewSet)
router.register(r'stories', StoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
