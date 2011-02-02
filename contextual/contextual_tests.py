from django.db import models

from contextual.contextual_models import HostnameTestModel, QueryStringTestModel, \
                                         RefererTestModel

class BaseTest(object):
    """
    Subclass this BaseTest to create your own 
    contextual tests with related models.
    """

    # Tests should define their own model(s).
    requires_models = [] 

    def __init__(self, *args, **kwargs):
        """
        Makes sure the models required by the test are registed
        within the Django eco-system. They only need to be 
        required if they would otherwise go uninstalled.
        """
        self.config = kwargs
        for model in self.requires_models:
            models.register_models('contextual', model)

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
            return HostnameTestModel.objects.get(hostname__iexact=hostname)
        except HostnameTestModel.DoesNotExist:
            return None


class QueryStringTest(BaseTest):

    requires_models = [QueryStringTestModel]


class RefererTest(BaseTest):

    requires_models = [RefererTestModel]
