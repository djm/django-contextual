from django.conf import settings

from contextual import LOADED_TESTS

class ContextualMiddleware(object):
    """
    The middleware used to provide the contextual
    analysis during post_request and the replacement
    of response data during process_response. 
    """
    def process_request(self, request):
        # For those serving media via django for development purposes;
        # this stops us from processing the media requests.
        if settings.DEBUG and request.path.startswith(settings.MEDIA_URL):
            return None
        # We now loop through the loaded tests, checking with each
        # one to see if it returns a match. As the tests are loaded
        # with a priority we can break out as soon as we find a match.
        for loaded_test in LOADED_TESTS:
            test_match = loaded_test.test(request)
            if test_match:
                break
        # If we found a matching test, then deal with it!
        if test_match:
            request.replacements = test_match.replacements.all()
        return None

    def process_response(self, request, response):
        """
        Carry out any replacements that were attached to the
        request object.
        """
        # If the request object has a replacements attribute
        # then replacements were definitely set. We also check
        # to make sure 'html' is in the mimetype being returned.
        # I think this is OK to deal with our text responses
        # but please feel free to point out an edge case I've
        # forgotten about.
        if hasattr(request, 'replacements') and \
                'html' in response['content-type']:
            import ipdb; ipdb.set_trace();
        return response
