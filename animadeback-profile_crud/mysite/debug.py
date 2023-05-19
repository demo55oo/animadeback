class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Debug code to print the authentication headers
        print('Authentication headers:', request.META.get('HTTP_AUTHORIZATION'))

        response = self.get_response(request)
        print(response)

        return response