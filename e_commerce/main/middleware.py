import re

from django.http import HttpRequest, HttpResponse


class CheckMobileMiddleware:
    """This middleware class checks is a request sent from a mobile device and
    sets bool flag about it.
    """

    def __init__(self, get_response: HttpRequest) -> None:
        self.get_response = get_response
        self.mobile_agent_regexp = re.compile(
            r".*(iphone|mobile|androidtouch)", re.IGNORECASE
        )

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if self.mobile_agent_regexp.match(request.META["HTTP_USER_AGENT"]):
            request.is_mobile = True
        else:
            request.is_mobile = False

        response = self.get_response(request)

        return response
