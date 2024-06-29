from django.views.generic import DetailView

from .models import Entity


class HtmxMixin:
    """Switches template depending on request.htmx"""

    def get_template_names(self) -> list[str]:
        if not self.request.htmx:
            return [self.template_name.replace("htmx/", "")]
        return [self.template_name]


class EntityDetailView(HtmxMixin, DetailView):
    model = Entity
    template_name = "entities/htmx/entity_detail.html"
