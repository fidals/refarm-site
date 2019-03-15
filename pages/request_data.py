import typing

from django import http


class Request:
    """Comprehensive request entity: django's request + url arguments."""

    def __init__(
        self, request: http.HttpRequest, url_kwargs: typing.Dict[str, str]
    ):
        """:param request: came here throw django urls and django views."""
        self.request = request
        self.url_kwargs = url_kwargs
