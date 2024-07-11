import json  # noqa

import pytest
import time_machine
from django.utils.http import urlencode  # noqa
from mocket import mocketize
from mocket.mockhttp import Entry  # noqa
from pytest_django.asserts import assertTemplateUsed  # noqa


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
