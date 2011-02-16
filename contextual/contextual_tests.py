import re
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.http import QueryDict
from urlparse import urlparse

from contextual.defaults import SEARCH_ENGINES
from contextual.contextual_models import (HostnameTestModel, QueryStringTestModel,
                                   RefererTestModel, BrandedSearchRefererTestModel)

class BaseTest(object):
    """
    Subclass this BaseTest to create your own 
    contextual tests with related models.
    """

    # Tests should define their own model(s)
    # for registration.
    requires_models = [] 
    requires_config_keys = {}

    def __init__(self, config=None):
        """
        Makes sure the models required by the test are registed
        within the Django eco-system. They only need to be 
        required if they would otherwise go uninstalled.
        """
        self.config = config
        for model in self.requires_models:
            # Register with Django's model system.
            models.register_models('contextual', model)
            try:
                # Register the models with Django's admin system.
                # Testing raises AlreadyRegistered as I guess the 
                # class is instantiated twice. Let me know a better way.
                admin.site.register(model)
            except admin.sites.AlreadyRegistered:
                pass
        # Now we test the passed in config dictionary had all
        # the necessary for configuration keys.
        for key, reason in self.requires_config_keys.iteritems():
            if not key in self.config:
                raise ImproperlyConfigured, \
                    "%s requires the key \"%s\" in its config dictionary: %s" % \
                            (self.__class__.__name__, key, reason)
    def _lookup_test(self, request):
        """ 
        Finds a matching rule based upon this test and the
        request and returns the rule if found else None.
        """
        raise NotImplementedError

    def test(self, request):
        """
        This is the method that should be called from the
        outside. It calls a sibling method to work out if
        we have a rule hit, and if so returns the replacement
        rules attached to it, else None.
        """
        rule = self.lookup_test(request)
        return rule.replacements.all() if rule else None


class HostnameTest(BaseTest):
    """
    This test uses the request.get_host() function
    to do a simple lookup on the hostname with the 
    relevant model to see if we get an exact match.
    """

    requires_models = [HostnameTestModel]

    def test(self, request):
        hostname = request.get_host()
        try:
            match =  HostnameTestModel.objects.get(hostname__iexact=hostname)
        except HostnameTestModel.DoesNotExist:
            match =  None
        return match


class QueryStringTest(BaseTest):
    """
    This test uses a config dictonary during
    instantiation to check a specific key
    of a query string for a specific value.
    If found, returns the match.
    """

    requires_models = [QueryStringTestModel]
    requires_config_keys = {
                'get_key': "Used to select the GET key to do the lookup on.",
            }

    def test(self, request):
        match = None
        key = self.config.get('get_key')
        # If that query string key has been set on the request.
        value = request.GET.get(key)
        if value:
            try:
                match = QueryStringTestModel.objects.get(value__iexact=value)
            except QueryStringTestModel.DoesNotExist:
                pass
        return match


class RefererTest(BaseTest):
    """
    This is a simple domain referer test, checks the
    referer URL for a match without our models.
    """

    requires_models = [RefererTestModel]

    def test(self, request):
        match = None
        referer = request.META.get('HTTP_REFERER')
        if referer:
            parsed_referer = urlparse(referer)
            try:
                match = RefererTestModel.objects.get(
                        domain__icontains=parsed_referer.hostname)
            except RefererTestModel.DoesNotExist:
                pass
        return match


class BrandedSearchRefererTest(BaseTest):
    """
    This test class checks whether the referer was a search
    engine and if so checks the query to see if it contains
    any of the "branded" terms specified in the instantiation
    config dictionary.
    """

    requires_models = [BrandedSearchRefererTestModel]
    requires_config_keys = {
        'brand_terms': "A list of regex strings classed as 'brand terms'.",
    }

    def __init__(self, *args, **kwargs):
        """
        Override the init so we can precompile the brand term 
        regex's on instantiation and therefore only do that once.
        """
        super(BrandedSearchRefererTest, self).__init__(*args, **kwargs)
        self.compiled_brand_terms = []
        for term in self.config['brand_terms']:
            compiled = re.compile(term, re.IGNORECASE|re.UNICODE)
            self.compiled_brand_terms.append(compiled)

    def test(self, request):
        match = None
        referer = request.META.get('HTTP_REFERER')
        if referer:
            url = urlparse(referer)
            for engine, lookup_key in SEARCH_ENGINES.iteritems():
                if engine in url.hostname:
                    query_string = QueryDict(url.query)
                    query = query_string.get(lookup_key)
                    match = self.get_match(engine, query)
                    break
        return match

    def get_match(self, search_engine, query):
        """
        Returns a test match using the search engine
        and search term used. 
        """
        branded = self.is_branded(query)
        try:
            return BrandedSearchRefererTestModel.objects.get(
                    search_engine=search_engine,
                    branded=branded)
        except BrandedSearchRefererTestModel.DoesNotExist:
            return None
             
    def is_branded(self, query):
        """
        Returns True if any of the words within
        the query are branded terms as defined
        by the config dictionary.
        """
        for term in self.compiled_brand_terms:
            if term.match(query):
                return True
        return False
