from django.forms import CharField, ModelForm, TextInput
from django.urls import reverse
from django.views.generic import CreateView, DetailView, UpdateView

from .models import Entity


class HtmxMixin:
    """Switches template depending on request.htmx"""

    def get_template_names(self) -> list[str]:
        if not self.request.htmx:
            return [self.template_name.replace("htmx/", "")]
        return [self.template_name]


class EntityCreateForm(ModelForm):
    class Meta:
        model = Entity
        fields = ("title", "description")


class EntityCreateView(HtmxMixin, CreateView):
    model = Entity
    form_class = EntityCreateForm
    template_name = "entities/htmx/entity_create.html"

    def get_success_url(self):
        return reverse("entities:entity_update", kwargs={"pk": self.object.id})


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


class EntityUpdateView(HtmxMixin, UpdateView):
    model = Entity
    form_class = EntityUpdateForm
    template_name = "entities/htmx/entity_update.html"

    def get_success_url(self):
        return reverse("entities:entity_detail", kwargs={"pk": self.object.id})


class EntityDetailView(HtmxMixin, DetailView):
    model = Entity
    template_name = "entities/htmx/entity_detail.html"
