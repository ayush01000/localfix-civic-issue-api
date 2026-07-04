from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, IssueViewSet


router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('issues', IssueViewSet, basename='issue')


urlpatterns = [
    path('', include(router.urls)),
]