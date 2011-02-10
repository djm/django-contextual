import re
from django.conf import settings
from django.core.urlresolvers import reverse

from contextual import LOADED_TESTS
from contextual.defaults import REPLACEMENT_TAGS

class ContextualMiddleware(object):
    """
    The middleware used to provide the contextual
    analysis during post_request and the replacement
    of response data during process_response. 
    """
    def process_request(self, request):
        # For those serving media via django for development purposes;
        # this stops us from processing the media requests. Also 
        # stops it from working for admin requests.
        if any([request.path.startswith(settings.MEDIA_URL),
                request.path.startswith(reverse('admin:index'))]):
            return None
        # We now loop through the loaded tests, checking with each
        # one to see if it returns a match. As the tests are loaded
        # with a priority we can break out as soon as we find a match.
        for loaded_test in LOADED_TESTS:
            test_match = loaded_test.test(request)
            if test_match:
                # If we found a matching test, then deal with it!
                request.contextual_test = test_match
                break
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
        # but please to point out an edge case I've forgotten about.
        if hasattr(request, 'contextual_test') and 'html' in response['content-type']:
            replacements = request.contextual_test.replacements.all()
            for replacement in replacements:
                raw_bracketed_tag = r"\[%s\]" % replacement.tag
                # Replace the given tags with the given data.
                response.content = re.sub(raw_bracketed_tag, replacement.data,
                                          response.content.decode('utf-8'),
                                          re.UNICODE)
        return response
