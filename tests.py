import json  # noqa

import pytest
import time_machine
from django.utils.http import urlencode  # noqa
from mocket import mocketize
from mocket.mockhttp import Entry  # noqa
from pytest_django.asserts import assertTemplateUsed

from djaframe.models import Entity, Scene, Staging


@mocketize(strict_mode=True)
@pytest.mark.django_db()
def test_root_url_status_code(client):
    with time_machine.travel("2024-07-11T17:46:55"):
        response = client.get(
            "/",
            "",
            HTTP_COOKIE="csrftoken=l6nepIuec7RFIFJCOVvb80YWODcCKQvv; sessionid=7hy0956ew6j35d809bams09onsncp6sf",  # noqa
            HTTP_PRIORITY="u=0, i",
            content_type="text/plain",
        )

        assert response.status_code == 302


@mocketize(strict_mode=True)
@pytest.mark.django_db()
def test_scene_list_view(client):
    with time_machine.travel("2024-07-11T18:25:35"):
        scene, _created = Scene.objects.get_or_create(
            title="First scene",
            description="This is the first scene cool go",
            defaults={
                "id": 1,
            },
        )

        response = client.get(
            "/3D/scene/list/",
            "",
            HTTP_COOKIE="csrftoken=l6nepIuec7RFIFJCOVvb80YWODcCKQvv; sessionid=7hy0956ew6j35d809bams09onsncp6sf; ph_phc_zQM74CuK5pp8UqgLvLlUF1yU38gp4XUAw9JLfp03fK3_posthog=%7B%22distinct_id%22%3A%22andy.war1965%40gmail.com%22%2C%22%24sesid%22%3A%5B1720722292446%2C%220190a30a-6d89-771c-9083-b055502babe7%22%2C1720722288009%5D%2C%22%24epp%22%3Atrue%7D",  # noqa
            HTTP_PRIORITY="u=0, i",
            content_type="text/plain",
        )

        assert response.status_code == 200
        assertTemplateUsed(response, "djaframe/scene_list.html")
        assertTemplateUsed(response, "djaframe/base_list.html")
        assertTemplateUsed(response, "base.html")
        assertTemplateUsed(response, "djaframe/htmx/scene_list.html")


@mocketize(strict_mode=True)
@pytest.mark.django_db()
def test_scene_detail_view(client):
    with time_machine.travel("2024-07-12T15:35:28"):
        scene, _created = Scene.objects.get_or_create(
            title="First scene",
            description="This is the first scene cool go down",
            defaults={
                "id": 1,
            },
        )
        entity, _created = Entity.objects.get_or_create(
            title="Sirena",
            description="Una sirena dormiente",
            obj_model="uploads/djaframe/obj/3/sirena.obj",
            mtl_model="",
            switch=True,
            color="#004080",
            defaults={
                "id": 3,
            },
        )
        entity_2, _created = Entity.objects.get_or_create(
            title="Sirena arancione",
            description="",
            obj_model="uploads/djaframe/obj/4/sirena.obj",
            mtl_model="",
            switch=True,
            color="#ff8000",
            defaults={
                "id": 4,
            },
        )
        staging, _created = Staging.objects.get_or_create(
            scene=scene,
            entity=entity,
            x_pos=-3.0,
            z_pos=0.0,
            rotation=60.0,
            defaults={
                "id": 1,
            },
        )
        staging_2, _created = Staging.objects.get_or_create(
            scene=scene,
            entity=entity_2,
            x_pos=0.0,
            z_pos=0.0,
            rotation=0.0,
            defaults={
                "id": 5,
            },
        )

        response = client.get(
            "/3D/scene/1/",
            "",
            HTTP_HX_REQUEST="true",
            HTTP_HX_TARGET="content",
            HTTP_HX_CURRENT_URL="http://127.0.0.1:8000/3D/scene/1/update/",
            HTTP_X_CSRFTOKEN="bMrvMbz1k5ySGFed0Yogw17WNGW3zIxsSWMQfnkI1KvguKj2OXc0XQZsqaHWMYeZ",  # noqa
            HTTP_COOKIE="csrftoken=RkvvDmVRRP7yYffZY9YUBZ2GNEV3nqRH; ph_phc_zQM74CuK5pp8UqgLvLlUF1yU38gp4XUAw9JLfp03fK3_posthog=%7B%22distinct_id%22%3A%22andy.war1965%40gmail.com%22%2C%22%24sesid%22%3A%5B1720722360538%2C%220190a30a-6d89-771c-9083-b055502babe7%22%2C1720722288009%5D%2C%22%24epp%22%3Atrue%7D",  # noqa
            HTTP_PRIORITY="u=0",
            content_type="text/plain",
        )

        assert response.status_code == 200
        assertTemplateUsed(response, "djaframe/htmx/scene_detail.html")


@mocketize(strict_mode=True)
@pytest.mark.django_db()
def test_scene_update_view_get(client):
    with time_machine.travel("2024-07-12T15:35:18"):
        scene, _created = Scene.objects.get_or_create(
            title="First scene",
            description="This is the first scene cool go down",
            defaults={
                "id": 1,
            },
        )
        entity, _created = Entity.objects.get_or_create(
            title="Sirena",
            description="Una sirena dormiente",
            obj_model="uploads/djaframe/obj/3/sirena.obj",
            mtl_model="",
            switch=True,
            color="#004080",
            defaults={
                "id": 3,
            },
        )

        staging, _created = Staging.objects.get_or_create(
            scene=scene,
            entity=entity,
            x_pos=-3.0,
            z_pos=0.0,
            rotation=60.0,
            defaults={
                "id": 1,
            },
        )

        response = client.get(
            "/3D/scene/1/update/",
            "",
            HTTP_HX_REQUEST="true",
            HTTP_HX_TARGET="content",
            HTTP_HX_CURRENT_URL="http://127.0.0.1:8000/3D/scene/list/",
            HTTP_X_CSRFTOKEN="bMrvMbz1k5ySGFed0Yogw17WNGW3zIxsSWMQfnkI1KvguKj2OXc0XQZsqaHWMYeZ",  # noqa
            HTTP_COOKIE="csrftoken=RkvvDmVRRP7yYffZY9YUBZ2GNEV3nqRH; ph_phc_zQM74CuK5pp8UqgLvLlUF1yU38gp4XUAw9JLfp03fK3_posthog=%7B%22distinct_id%22%3A%22andy.war1965%40gmail.com%22%2C%22%24sesid%22%3A%5B1720722360538%2C%220190a30a-6d89-771c-9083-b055502babe7%22%2C1720722288009%5D%2C%22%24epp%22%3Atrue%7D",  # noqa
            HTTP_PRIORITY="u=0",
            content_type="text/plain",
        )

        assert response.status_code == 200
        assertTemplateUsed(response, "djaframe/htmx/scene_update.html")


@mocketize(strict_mode=True)
@pytest.mark.django_db()
def test_scene_update_view_post(client):
    with time_machine.travel("2024-07-12T15:35:28"):
        scene, _created = Scene.objects.get_or_create(
            title="First scene",
            description="This is the first scene cool go down",
            defaults={
                "id": 1,
            },
        )

        response = client.post(
            "/3D/scene/1/update/",
            urlencode(
                {
                    "title": "First scene",
                    "description": "This is the first scene cool go down",
                }
            ),
            HTTP_HX_REQUEST="true",
            HTTP_HX_TARGET="content",
            HTTP_HX_CURRENT_URL="http://127.0.0.1:8000/3D/scene/1/update/",
            HTTP_X_CSRFTOKEN="bMrvMbz1k5ySGFed0Yogw17WNGW3zIxsSWMQfnkI1KvguKj2OXc0XQZsqaHWMYeZ",  # noqa
            HTTP_COOKIE="csrftoken=RkvvDmVRRP7yYffZY9YUBZ2GNEV3nqRH; ph_phc_zQM74CuK5pp8UqgLvLlUF1yU38gp4XUAw9JLfp03fK3_posthog=%7B%22distinct_id%22%3A%22andy.war1965%40gmail.com%22%2C%22%24sesid%22%3A%5B1720722360538%2C%220190a30a-6d89-771c-9083-b055502babe7%22%2C1720722288009%5D%2C%22%24epp%22%3Atrue%7D",  # noqa
            HTTP_PRIORITY="u=0",
            content_type="application/x-www-form-urlencoded",
        )

        assert response.status_code == 302

        scene.refresh_from_db()
        assert scene.title == "First scene"
        assert scene.description == "This is the first scene cool go down"


@mocketize(strict_mode=True)
@pytest.mark.django_db()
def test_staging_add_view_get(client):
    with time_machine.travel("2024-07-12T15:35:26"):
        scene, _created = Scene.objects.get_or_create(
            title="First scene",
            description="This is the first scene cool go down",
            defaults={
                "id": 1,
            },
        )
        entity, _created = Entity.objects.get_or_create(
            title="Sirena",
            description="Una sirena dormiente",
            obj_model="uploads/djaframe/obj/3/sirena.obj",
            mtl_model="",
            switch=True,
            color="#004080",
            defaults={
                "id": 3,
            },
        )
        entity_2, _created = Entity.objects.get_or_create(
            title="Sirena arancione",
            description="",
            obj_model="uploads/djaframe/obj/4/sirena.obj",
            mtl_model="",
            switch=True,
            color="#ff8000",
            defaults={
                "id": 4,
            },
        )

        staging, _created = Staging.objects.get_or_create(
            scene=scene,
            entity=entity,
            x_pos=-3.0,
            z_pos=0.0,
            rotation=60.0,
            defaults={
                "id": 1,
            },
        )
        staging_2, _created = Staging.objects.get_or_create(
            scene=scene,
            entity=entity_2,
            x_pos=0.0,
            z_pos=0.0,
            rotation=0.0,
            defaults={
                "id": 5,
            },
        )

        response = client.get(
            "/3D/scene/1/staging-add/",
            "",
            HTTP_HX_REQUEST="true",
            HTTP_HX_TARGET="staged-entities",
            HTTP_HX_CURRENT_URL="http://127.0.0.1:8000/3D/scene/1/update/",
            HTTP_X_CSRFTOKEN="bMrvMbz1k5ySGFed0Yogw17WNGW3zIxsSWMQfnkI1KvguKj2OXc0XQZsqaHWMYeZ",  # noqa
            HTTP_COOKIE="csrftoken=RkvvDmVRRP7yYffZY9YUBZ2GNEV3nqRH; ph_phc_zQM74CuK5pp8UqgLvLlUF1yU38gp4XUAw9JLfp03fK3_posthog=%7B%22distinct_id%22%3A%22andy.war1965%40gmail.com%22%2C%22%24sesid%22%3A%5B1720722360538%2C%220190a30a-6d89-771c-9083-b055502babe7%22%2C1720722288009%5D%2C%22%24epp%22%3Atrue%7D",  # noqa
            HTTP_PRIORITY="u=0",
            content_type="text/plain",
        )

        assert response.status_code == 200
        assertTemplateUsed(response, "djaframe/htmx/staged_entity_loop.html")
        assertTemplateUsed(response, "djaframe/htmx/staging_detail.html")


@mocketize(strict_mode=True)
@pytest.mark.django_db()
def test_staging_add_view_post(client):
    with time_machine.travel("2024-07-12T15:35:26"):
        scene, _created = Scene.objects.get_or_create(
            title="First scene",
            description="This is the first scene cool go down",
            defaults={
                "id": 1,
            },
        )
        entity, _created = Entity.objects.get_or_create(
            title="Sirena arancione",
            description="",
            obj_model="uploads/djaframe/obj/4/sirena.obj",
            mtl_model="",
            switch=True,
            color="#ff8000",
            defaults={
                "id": 4,
            },
        )

        response = client.post(
            "/3D/scene/1/staging-add/",
            urlencode({"entity": "4", "x_pos": "0", "z_pos": "0", "rotation": "0"}),
            HTTP_HX_REQUEST="true",
            HTTP_HX_TARGET="staged-entities",
            HTTP_HX_CURRENT_URL="http://127.0.0.1:8000/3D/scene/1/update/",
            HTTP_X_CSRFTOKEN="bMrvMbz1k5ySGFed0Yogw17WNGW3zIxsSWMQfnkI1KvguKj2OXc0XQZsqaHWMYeZ",  # noqa
            HTTP_COOKIE="csrftoken=RkvvDmVRRP7yYffZY9YUBZ2GNEV3nqRH; ph_phc_zQM74CuK5pp8UqgLvLlUF1yU38gp4XUAw9JLfp03fK3_posthog=%7B%22distinct_id%22%3A%22andy.war1965%40gmail.com%22%2C%22%24sesid%22%3A%5B1720722360538%2C%220190a30a-6d89-771c-9083-b055502babe7%22%2C1720722288009%5D%2C%22%24epp%22%3Atrue%7D",  # noqa
            HTTP_PRIORITY="u=0",
            content_type="application/x-www-form-urlencoded",
        )

        assert response.status_code == 302

        staging = Staging.objects.get(
            scene=scene,
            entity=entity,
        )
        assert staging.x_pos == 0.0
        assert staging.z_pos == 0.0
        assert staging.rotation == 0.0


@mocketize(strict_mode=True)
@pytest.mark.django_db()
def test_entity_list_view(client):
    with time_machine.travel("2024-07-12T15:35:07"):
        entity, _created = Entity.objects.get_or_create(
            title="Sirena",
            description="Una sirena dormiente",
            obj_model="uploads/djaframe/obj/3/sirena.obj",
            mtl_model="",
            switch=True,
            color="#004080",
            defaults={
                "id": 3,
            },
        )
        entity_2, _created = Entity.objects.get_or_create(
            title="Sirena arancione",
            description="",
            obj_model="uploads/djaframe/obj/4/sirena.obj",
            mtl_model="",
            switch=True,
            color="#ff8000",
            defaults={
                "id": 4,
            },
        )

        response = client.get(
            "/3D/entity/list/",
            "",
            HTTP_HX_REQUEST="true",
            HTTP_HX_TARGET="content",
            HTTP_HX_CURRENT_URL="http://127.0.0.1:8000/3D/entity/4/",
            HTTP_X_CSRFTOKEN="bMrvMbz1k5ySGFed0Yogw17WNGW3zIxsSWMQfnkI1KvguKj2OXc0XQZsqaHWMYeZ",  # noqa
            HTTP_COOKIE="csrftoken=RkvvDmVRRP7yYffZY9YUBZ2GNEV3nqRH; ph_phc_zQM74CuK5pp8UqgLvLlUF1yU38gp4XUAw9JLfp03fK3_posthog=%7B%22distinct_id%22%3A%22andy.war1965%40gmail.com%22%2C%22%24sesid%22%3A%5B1720722360538%2C%220190a30a-6d89-771c-9083-b055502babe7%22%2C1720722288009%5D%2C%22%24epp%22%3Atrue%7D",  # noqa
            HTTP_PRIORITY="u=0",
            content_type="text/plain",
        )

        assert response.status_code == 200
        assertTemplateUsed(response, "djaframe/htmx/entity_list.html")
