import re
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse

from contextual import LOADED_TESTS
from contextual.defaults import SESSION_KEY
from contextual.models import ReplacementTag

class ContextualMiddleware(object):
    """
    The middleware used to provide the contextual
    analysis during post_request and the replacement
    of response data during process_response. 
    """

    def is_excludable(self, request):
        """
        Returns True if the request should be excluded
        from any contextual lookup or replacements.
        """
        # For those serving media via django for development purposes;
        # this stops us from processing the media requests. Also 
        # stops it from working for admin requests. We also
        # set a flag on the request so we can faster decide whether
        # or not to process in the response.
        return any([
            hasattr(request, 'contextual_excluded'),
            request.path.startswith(settings.MEDIA_URL),
            request.path.startswith(reverse('admin:index'))
        ])

    def is_overrideable(self, request):
        """
        Returns True if the request should be the decider
        for any match *despite* there already being a test
        match on the session.
        """
        # TODO: Implement this functionality.
        return False

    def process_request(self, request):
        """
        Carry out the processing of the incoming request to 
        calculate which, if any, replacements we need to apply
        to the response.
        """
        if self.is_excludable(request):
            # Set a flag so we can exclude this request faster
            # in the future (e.g during the response).
            request.contextual_excluded = True
            return None
        # Before we run the tests to check whether we have a match,
        # we check to see if we ALREADY have a match on the session.
        # We recommend the use of the cache backend for the session
        # to save on those precious DB queries (we don't care about
        # serious persistence however, you may). If we have a match
        # we also check whether the incoming request *should* override
        # the stored match. This relies on the test classes themselves.
        if SESSION_KEY in request.session and not self.is_overrideable(request):
            # We found a match, load on to the request and dump out.
            request.contextual_test = request.session.get(SESSION_KEY)
            return None
        # We now loop through the loaded tests, checking with each
        # one to see if it returns a match. As the tests are loaded
        # with a priority we can break out as soon as we find a match.
        for loaded_test in LOADED_TESTS:
            test_match = loaded_test.test(request)
            if test_match:
                # If we found a matching test, then deal with it!
                request.contextual_test = test_match
                # We also store on the session to future lookups
                # retain the same contextual data as the first
                # incoming request. TODO: Override functionality.
                request.session[SESSION_KEY] = test_match
                return None

    def process_response(self, request, response):
        """
        Carry out any replacements that were attached to the
        request object.
        """
        if self.is_excludable(request):
            return response
        # We check to make sure 'html' is in the content-type of
        # the response so that we don't fiddle with responses
        # we do not wish to touch. I think this is OK but please
        # point out an edge case if there is one.
        if 'html' in response['content-type']:
            # Get a cached copy of all the tags available or refresh cache.
            all_tags = cache.get('all_tags')
            if all_tags is None:
                all_tags = ReplacementTag.objects.all()
                cache.set('all_tags', all_tags, 300)
            if hasattr(request, 'contextual_test'):
                # We have to calculate which tags to use our contextual_test match
                # replacement data for and which ones to use the default replacement
                # text for. This is so we never get a tag going unreplaced. TODO: cache!
                replacements = request.contextual_test.replacements.filter(
                                                active=True, tag__in=all_tags)
                req_tags = [replacement.tag for replacement in replacements] 
            else:
                replacements = []
                req_tags = []
            # To get the defaults we want all replacements that are possible
            # minus the ones that are set on the request.
            defaults = set(all_tags) - set(req_tags)
            # Carry out the replacements for the defaults, if any,
            # and then the replacements we found a match for.
            for default in defaults:
                response = self.rewrite_response(response, default.raw_tag, 
                                                 default.default)
            for replacement in replacements:
                response = self.rewrite_response(response, replacement.tag.raw_tag,
                                                 replacement.data)
        return response

    def rewrite_response(self, response, raw_tag, replacement):
        """
        Given a response, a tag and some replacement data,
        this method carries out the regex substitution
        and returns the response.
        """
        response.content = re.sub(raw_tag, replacement,
                                  response.content.decode('utf-8'),
                                  re.UNICODE)
        return response
