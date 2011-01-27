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
        for model in self.requires_models:
            models.register_models('contextual', model)

    def test(self, request):
        """ 
        Finds a matching rule based upon this test and returns
        the replacements that should take place due to it.
        """
        raise NotImplementedError


class HostnameTest(BaseTest):

    requires_models = [HostnameTestModel]


class QueryStringTest(BaseTest):

    requires_models = [QueryStringTestModel]


class RefererTest(BaseTest):

    requires_models = [RefererTestModel]
