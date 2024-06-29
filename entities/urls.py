from django.urls import path

from .views import EntityDetailView

app_name = "entities"
urlpatterns = [
    path("<pk>/", EntityDetailView.as_view(), name="entity_detail"),
]
