from pathlib import Path
from typing import Any

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models.query import QuerySet
from django.forms import CharField, ModelForm, TextInput
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .models import Entity, MaterialImage, Scene, Staging


class HtmxMixin:
    """Switches template depending on request.htmx"""

    def get_template_names(self) -> list[str]:
        if not self.request.htmx:
            return [self.template_name.replace("htmx/", "")]
        return [self.template_name]


class HtmxOnlyMixin:
    """Denies request if no request.htmx"""

    def get_template_names(self) -> list[str]:
        if not self.request.htmx:
            raise Http404("Request without HTMX headers")
        return super().get_template_names()


class EntityListView(HtmxMixin, ListView):
    model = Entity
    template_name = "djaframe/htmx/entity_list.html"


class EntityUnstagedListView(HtmxMixin, ListView):
    model = Entity
    template_name = "djaframe/htmx/entity_unstaged_list.html"

    def get_queryset(self) -> QuerySet[Any]:
        staged = Staging.objects.values_list("entity", flat=True)
        staged = list(set(staged))
        qs = Entity.objects.exclude(id__in=staged)
        return qs


class EntityCreateForm(ModelForm):
    class Meta:
        model = Entity
        fields = ("title", "description")


class EntityCreateView(PermissionRequiredMixin, HtmxMixin, CreateView):
    model = Entity
    permission_required = "djaframe.add_entity"
    form_class = EntityCreateForm
    template_name = "djaframe/htmx/entity_create.html"

    def get_success_url(self):
        return reverse("djaframe:entity_update", kwargs={"pk": self.object.id})


class EntityUpdateForm(ModelForm):
    class Meta:
        model = Entity
        fields = (
            "title",
            "gltf_model",
            "obj_model",
            "mtl_model",
            "switch",
            "description",
        )


class MaterialImageCreateForm(ModelForm):
    class Meta:
        model = MaterialImage
        fields = ("image",)


class EntityUpdateView(PermissionRequiredMixin, HtmxMixin, UpdateView):
    model = Entity
    permission_required = "djaframe.change_entity"
    form_class = EntityUpdateForm
    template_name = "djaframe/htmx/entity_update.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["matimg_form"] = MaterialImageCreateForm()
        return context

    def get_success_url(self):
        return reverse("djaframe:entity_detail", kwargs={"pk": self.object.id})


class MaterialImageListView(HtmxOnlyMixin, DetailView):
    model = Entity
    template_name = "djaframe/htmx/material_image_loop.html"


@permission_required("djaframe.add_materialimage")
def material_image_create(request, pk):
    if not request.htmx:
        raise Http404("Request without HTMX headers")
    entity = get_object_or_404(Entity, id=pk)
    form = MaterialImageCreateForm()
    context = {"object": entity, "matimg_form": form}
    template_name = "djaframe/htmx/material_image_create.html"
    if request.method == "POST":
        form = MaterialImageCreateForm(request.POST, request.FILES)
        if form.is_valid():
            # create material image
            MaterialImage.objects.create(
                entity=entity,
                image=form.cleaned_data["image"],
            )
            return HttpResponseRedirect(
                reverse("djaframe:matimg_create", kwargs={"pk": entity.id})
                + "?refresh=True",
            )
        else:
            context["matimg_form"] = form
            context["invalid_form"] = True
    elif request.method == "GET" and "refresh" in request.GET:
        return TemplateResponse(
            request,
            template_name,
            context,
            headers={"HX-Trigger": "refreshImages"},
        )
    return TemplateResponse(
        request,
        template_name,
        context,
    )


@permission_required("djaframe.delete_materialimage")
def material_image_delete(request, pk):
    if not request.htmx:
        raise Http404("Request without HTMX headers")
    # get material image and prepare for template response
    matimg = get_object_or_404(MaterialImage, id=pk)
    context = {"object": matimg.entity}
    template_name = "djaframe/htmx/material_image_delete.html"
    # delete file and material image
    try:
        file = Path(matimg.image.path)
        if file.is_file():
            Path(file).unlink()
    except FileNotFoundError:
        pass
    matimg.delete()
    return TemplateResponse(
        request,
        template_name,
        context,
    )


class EntityDetailView(HtmxMixin, DetailView):
    model = Entity
    template_name = "djaframe/htmx/entity_detail.html"


@permission_required("djaframe.delete_entity")
def entity_delete(request, pk):
    if not request.htmx:
        raise Http404("Request without HTMX headers")
    # get entity and prepare for template response
    entity = get_object_or_404(Entity, id=pk)
    context = {}
    template_name = "djaframe/htmx/entity_delete.html"
    # delete entity
    entity.delete()
    return TemplateResponse(
        request,
        template_name,
        context,
    )


@permission_required("djaframe.delete_entity")
def entity_unstaged_delete(request):
    if not request.htmx:
        raise Http404("Request without HTMX headers")
    # get entities and prepare for template response
    staged = Staging.objects.values_list("entity", flat=True)
    staged = list(set(staged))
    # delete entities
    Entity.objects.exclude(id__in=staged).delete()
    context = {}
    template_name = "djaframe/htmx/entity_delete.html"
    return TemplateResponse(
        request,
        template_name,
        context,
    )


class SceneListView(HtmxMixin, ListView):
    model = Scene
    template_name = "djaframe/htmx/scene_list.html"


class SceneCreateForm(ModelForm):
    class Meta:
        model = Scene
        fields = ("title", "description", "dxf", "image")


class SceneCreateView(PermissionRequiredMixin, HtmxMixin, CreateView):
    model = Scene
    permission_required = "djaframe.add_scene"
    form_class = SceneCreateForm
    template_name = "djaframe/htmx/scene_create.html"

    def get_success_url(self):
        if self.object.dxf:
            return reverse("djaframe:scene_detail", kwargs={"pk": self.object.id})
        return reverse("djaframe:scene_update", kwargs={"pk": self.object.id})


class StagingCreateForm(ModelForm):
    color = CharField(
        label="Color",
        required=True,
        widget=TextInput(
            attrs={"class": "form-control form-control-color", "type": "color"}
        ),
    )

    class Meta:
        model = Staging
        fields = ("entity", "position", "rotation", "scale", "color")


class SceneUpdateView(PermissionRequiredMixin, HtmxMixin, UpdateView):
    model = Scene
    permission_required = "djaframe.change_scene"
    form_class = SceneCreateForm
    template_name = "djaframe/htmx/scene_update.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["staging_form"] = StagingCreateForm()
        return context

    def get_success_url(self):
        return reverse("djaframe:scene_detail", kwargs={"pk": self.object.id})


class StagingListView(HtmxOnlyMixin, DetailView):
    model = Scene
    template_name = "djaframe/htmx/staged_entity_loop.html"


@permission_required("djaframe.delete_scene")
def scene_delete(request, pk):
    if not request.htmx:
        raise Http404("Request without HTMX headers")
    # get scene and prepare for template response
    scene = get_object_or_404(Scene, id=pk)
    context = {}
    template_name = "djaframe/htmx/scene_delete.html"
    # delete scene
    scene.delete()
    return TemplateResponse(
        request,
        template_name,
        context,
    )


@permission_required("djaframe.add_staging")
def staged_entity_create(request, pk):
    if not request.htmx:
        raise Http404("Request without HTMX headers")
    scene = get_object_or_404(Scene, id=pk)
    form = StagingCreateForm()
    context = {"object": scene, "staging_form": form}
    template_name = "djaframe/htmx/staging_create.html"
    if request.method == "POST":
        form = StagingCreateForm(request.POST)
        if form.is_valid():
            # create staged entity
            Staging.objects.create(
                scene=scene,
                entity=form.cleaned_data["entity"],
                position=form.cleaned_data["position"],
                scale=form.cleaned_data["scale"],
                rotation=form.cleaned_data["rotation"],
            )
            return HttpResponseRedirect(
                reverse("djaframe:staging_create", kwargs={"pk": scene.id})
                + "?refresh=True",
            )
        else:
            context["staging_form"] = form
            context["invalid_form"] = True
    elif request.method == "GET" and "refresh" in request.GET:
        return TemplateResponse(
            request,
            template_name,
            context,
            headers={"HX-Trigger": "refreshStagings"},
        )
    return TemplateResponse(
        request,
        template_name,
        context,
    )


class SceneDetailView(HtmxMixin, DetailView):
    model = Scene
    template_name = "djaframe/htmx/scene_detail.html"


class StagingDetailView(DetailView):
    model = Staging
    context_object_name = "staging"
    template_name = "djaframe/htmx/staging_detail.html"

    def get_template_names(self) -> list[str]:
        if not self.request.htmx:
            raise Http404("Request without HTMX headers")
        return super().get_template_names()


class StagingUpdateView(PermissionRequiredMixin, HtmxOnlyMixin, UpdateView):
    model = Staging
    permission_required = "djaframe.change_staging"
    form_class = StagingCreateForm
    template_name = "djaframe/htmx/staging_update.html"

    def get_success_url(self):
        return reverse("djaframe:staging_detail", kwargs={"pk": self.object.id})


@permission_required("djaframe.delete_staging")
def staging_delete(request, pk):
    if not request.htmx:
        raise Http404("Request without HTMX headers")
    # get staging and prepare for template response
    staging = get_object_or_404(Staging, id=pk)
    context = {"object": staging.scene}
    template_name = "djaframe/htmx/staging_delete.html"
    # delete staging
    staging.delete()
    return TemplateResponse(
        request,
        template_name,
        context,
    )
