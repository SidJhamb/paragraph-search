"""
URL mappings for the paragraph APIs.
"""
from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter

from paragraph import views

app_name = 'paragraph'

router = DefaultRouter()
router.register('search', views.ParagraphListViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('get', views.ParagraphCreateView.as_view(), name='create'),
    path('dictionary', views.DictionaryRetrieveView.as_view(), name='dict'),
]
