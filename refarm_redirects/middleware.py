from django.conf import settings
from django.contrib.redirects.models import Redirect
from django.contrib.redirects.middleware \
    import RedirectFallbackMiddleware \
    as DjangoRedirectFallbackMiddleware
from django.contrib.sites.shortcuts import get_current_site


class RedirectAllMiddleware(DjangoRedirectFallbackMiddleware):
    # reloaded this method
    # just to drop `response.status_code` status check
    # in base class
    def process_response(self, request, response):
        full_path = request.get_full_path()
        current_site = get_current_site(request)

        r = None
        try:
            r = Redirect.objects.get(site=current_site, old_path=full_path)
        except Redirect.DoesNotExist:
            pass
        if r is None and settings.APPEND_SLASH and not request.path.endswith('/'):
            try:
                r = Redirect.objects.get(
                    site=current_site,
                    old_path=request.get_full_path(force_append_slash=True),
                )
            except Redirect.DoesNotExist:
                pass
        if r is not None:
            if r.new_path == '':
                return self.response_gone_class()
            return self.response_redirect_class(r.new_path)

        # No redirect was found. Return the response.
        return response
