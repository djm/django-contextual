from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.db import models

from contextual.contextual_models import HostnameTestModel, QueryStringTestModel, \
                                         RefererTestModel

class BaseTest(object):
    """
    Subclass this BaseTest to create your own 
    contextual tests with related models.
    """

    # Tests should define their own model(s)
    # for registration.
    requires_models = [] 
    requires_config_keys = {}

    def __init__(self, *args, **kwargs):
        """
        Makes sure the models required by the test are registed
        within the Django eco-system. They only need to be 
        required if they would otherwise go uninstalled.
        """
        self.config = kwargs
        for model in self.requires_models:
            # Register with Django's model system.
            models.register_models('contextual', model)
            # Register the models with Django's admin system.
            admin.site.register(model)
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

    requires_models = [RefererTestModel]
