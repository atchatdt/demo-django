# https://docs.djangoproject.com/en/3.1/topics/http/middleware/
# https://stackoverflow.com/questions/18322262/how-to-set-up-custom-middleware-in-django
def simple_middleware(get_response):
    # One-time configuration and initialization.
    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = get_response(request)
        print('*'*30)
        # Code to be executed for each request/response after
        # the view is called.

        return response
    return middleware
