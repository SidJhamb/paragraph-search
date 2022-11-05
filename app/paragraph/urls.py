"""
URL mappings for the text API.
"""
from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter

from paragraph import views


app_name = 'text'

router = DefaultRouter()
router.register('search', views.ParagraphListViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('get', views.ParagraphCreateView.as_view(), name='create'),
    #path('get/<int:pk>/', views.ParagraphRetrieveView.as_view()),
    #path('get/(?P<id>.+)/$', views.ParagraphListView.as_view()),
]