from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe import views


# Generate urls from view
router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)

# Lookup for reverse function
app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))  # all paths that match the recipe app
]
