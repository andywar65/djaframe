from pathlib import Path
from typing import Any

from django.forms import CharField, ModelForm, TextInput
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .models import Entity, MaterialImage


class HtmxMixin:
    """Switches template depending on request.htmx"""

    def get_template_names(self) -> list[str]:
        if not self.request.htmx:
            return [self.template_name.replace("htmx/", "")]
        return [self.template_name]


class EntityListView(HtmxMixin, ListView):
    model = Entity
    template_name = "djaframe/htmx/entity_list.html"


class EntityCreateForm(ModelForm):
    class Meta:
        model = Entity
        fields = ("title", "description")


class EntityCreateView(HtmxMixin, CreateView):
    model = Entity
    form_class = EntityCreateForm
    template_name = "djaframe/htmx/entity_create.html"

    def get_success_url(self):
        return reverse("djaframe:entity_update", kwargs={"pk": self.object.id})


class EntityUpdateForm(ModelForm):
    color = CharField(
        label="Color",
        required=True,
        widget=TextInput(
            attrs={"class": "form-control form-control-color", "type": "color"}
        ),
    )

    class Meta:
        model = Entity
        fields = ("title", "obj_model", "mtl_model", "switch", "color", "description")


class MaterialImageCreateForm(ModelForm):
    class Meta:
        model = MaterialImage
        fields = ("image",)


class EntityUpdateView(HtmxMixin, UpdateView):
    model = Entity
    form_class = EntityUpdateForm
    template_name = "djaframe/htmx/entity_update.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["matimg_form"] = MaterialImageCreateForm()
        return context

    def get_success_url(self):
        return reverse("djaframe:entity_detail", kwargs={"pk": self.object.id})


def material_image_create(request, pk):
    if not request.htmx:
        raise Http404("Request without HTMX headers")
    entity = get_object_or_404(Entity, pk=pk)
    form = MaterialImageCreateForm()
    context = {"object": entity, "matimg_form": form}
    template_name = "djaframe/htmx/material_image_loop.html"
    if request.method == "POST":
        form = MaterialImageCreateForm(request.POST, request.FILES)
        if form.is_valid():
            # create material image
            MaterialImage.objects.create(
                entity=entity,
                image=form.cleaned_data["image"],
            )
            return HttpResponseRedirect(
                reverse("djaframe:matimg_create", kwargs={"pk": entity.id}),
            )
        else:
            context["matimg_form"] = form
            context["invalid_form"] = True
    return TemplateResponse(
        request,
        template_name,
        context,
    )


def material_image_delete(request, pk):
    if not request.htmx:
        raise Http404("Request without HTMX headers")
    # get material image and prepare for template response
    matimg = get_object_or_404(MaterialImage, pk=pk)
    form = MaterialImageCreateForm()
    context = {"object": matimg.entity, "matimg_form": form}
    template_name = "djaframe/htmx/material_image_loop.html"
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


def entity_delete(request, pk):
    if not request.htmx:
        raise Http404("Request without HTMX headers")
    # get entity and prepare for template response
    entity = get_object_or_404(Entity, pk=pk)
    context = {}
    template_name = "djaframe/htmx/entity_delete.html"
    # delete entity
    entity.delete()
    return TemplateResponse(
        request,
        template_name,
        context,
    )
