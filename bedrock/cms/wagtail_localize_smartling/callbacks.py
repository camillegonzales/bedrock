# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# This file contains callback functions to be called by
# github.com/mozilla/wagtail-localize-smartling/ and
# hooked in via settings.
#
# The README.md of that repo covers what inputs are
# provided and what outputs are needed

from typing import TYPE_CHECKING

from django.test import RequestFactory

from wagtail.models import Page
from wagtail_localize_smartling.exceptions import IncapableVisualContextCallback

if TYPE_CHECKING:
    from wagtail_localize_smartling.models import Job

from wagtaildraftsharing.models import WagtaildraftsharingLink
from wagtaildraftsharing.views import SharingLinkView


def _get_html_for_sharing_link(sharing_link: WagtaildraftsharingLink) -> str:
    request = RequestFactory().get(sharing_link.url)
    view_func = SharingLinkView.as_view()
    resp = view_func(
        request=request,
        key=sharing_link.key,
    )
    return resp.content.decode("utf-8")


def _get_full_url_for_sharing_link(sharing_link: WagtaildraftsharingLink, page: "Page") -> str:
    return f"{page.get_site().root_url}{sharing_link.url}"


def visual_context(smartling_job: "Job") -> tuple[str, str]:
    # Needs to return two strings:
    # 1. A URL where the content object (usually a Page; possibly a draft one)
    #    can be viewed _without authentication_
    # 2. The HTML of the state of the page at this point in time

    content_obj = smartling_job.translation_source.get_source_instance()

    if not isinstance(content_obj, Page):
        # We can currently only supply visual context for Pages, but not for
        # other things like Snippets, so return early and show there's nothing
        # to be processed
        raise IncapableVisualContextCallback("Object was not visually previewable")

    revision = content_obj.latest_revision

    sharing_link = WagtaildraftsharingLink.objects.get_or_create_for_revision(
        revision=revision,
        user=smartling_job.user,
    )

    url = _get_full_url_for_sharing_link(sharing_link=sharing_link, page=content_obj)
    html = _get_html_for_sharing_link(sharing_link=sharing_link)

    return (url, html)
