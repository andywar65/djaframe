from django.urls import path

from .views import (
    EntityCreateView,
    EntityDetailView,
    EntityListView,
    EntityUpdateView,
    MaterialImageListView,
    SceneCreateView,
    SceneDetailView,
    SceneListView,
    SceneUpdateView,
    StagingDetailView,
    StagingListView,
    StagingUpdateView,
    entity_delete,
    material_image_create,
    material_image_delete,
    scene_delete,
    staged_entity_create,
    staging_delete,
)

app_name = "djaframe"
urlpatterns = [
    path("entity/list/", EntityListView.as_view(), name="entity_list"),
    path("entity/add/", EntityCreateView.as_view(), name="entity_create"),
    path("entity/<pk>/", EntityDetailView.as_view(), name="entity_detail"),
    path("entity/<pk>/update/", EntityUpdateView.as_view(), name="entity_update"),
    path("entity/<pk>/delete/", entity_delete, name="entity_delete"),
    path("entity/<pk>/matimg/add/", material_image_create, name="matimg_create"),
    path(
        "entity/<pk>/matimg/list/", MaterialImageListView.as_view(), name="matimg_list"
    ),
    path("matimg/<pk>/", material_image_delete, name="matimg_delete"),
    path("scene/list/", SceneListView.as_view(), name="scene_list"),
    path("scene/add/", SceneCreateView.as_view(), name="scene_create"),
    path("scene/<pk>/", SceneDetailView.as_view(), name="scene_detail"),
    path("scene/<pk>/update/", SceneUpdateView.as_view(), name="scene_update"),
    path("scene/<pk>/delete/", scene_delete, name="scene_delete"),
    path("scene/<pk>/staging/add/", staged_entity_create, name="staging_create"),
    path("scene/<pk>/staging/list/", StagingListView.as_view(), name="staging_list"),
    path("staging/<pk>/", StagingDetailView.as_view(), name="staging_detail"),
    path("staging/<pk>/update/", StagingUpdateView.as_view(), name="staging_update"),
    path("staging/<pk>/delete/", staging_delete, name="staging_delete"),
]
