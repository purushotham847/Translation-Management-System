from django.http import HttpResponseForbidden


class ChromeOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Check if the browser is Chrome
        if 'Chrome/' in user_agent and 'Chromium' not in user_agent:
            return self.get_response(request)

        # Deny access for non-Chrome browsers
        return HttpResponseForbidden(
            "<h1>Access Denied</h1><p>This application is accessible only via Google Chrome.</p>"
        )
