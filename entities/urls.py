from django.urls import path

from .views import EntityCreateView, EntityDetailView

app_name = "entities"
urlpatterns = [
    path("entity/add/", EntityCreateView.as_view(), name="entity_create"),
    path("entity/<pk>/", EntityDetailView.as_view(), name="entity_detail"),
]
