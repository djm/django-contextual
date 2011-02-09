from django.core.handlers.wsgi import WSGIRequest
from django.test import TestCase
from django.test import Client

#from contextual.contextual_models import HostnameTestModel
#from contextual.contextual_tests import HostnameTest
#from contextual.models import *


default_environ = {
    'PATH_INFO': '/',
    'QUERY_STRING': '',
    'REQUEST_METHOD': 'GET',
    'SCRIPT_NAME': '',
    'SERVER_NAME': 'testserver',
    'SERVER_PORT': 80,
    'SERVER_PROTOCOL': 'HTTP/1.1',
}

class RequestFactory(Client):
    """
    Class that lets you create mock Request objects for use in testing.
    
    Adapted from http://djangosnippets.org/snippets/963/
    
    """

    def __init__(self, environ=default_environ, *args, **kwargs):
        self.environ = environ
        super(RequestFactory, self).__init__(*args, **kwargs)
        self.environ['HTTP_COOKIE'] = self.cookies

    def request(self, **request):
        """
        Similar to parent class, but returns the request object as 
        soon as it has created it.
        """
        environ = default_environ
        environ.update(self.defaults)
        environ.update(request)
        return WSGIRequest(environ)


class BaseTestCase(TestCase):

    def setUp(self):
        """
        Install some replacement values so we can add
        them to our rules later.
        """
        pass


class HostnameRequestTest(BaseTestCase):

    def setUp(self):
        super(HostnameRequestTest, self).setUp()
    
    def a_test():
        assert 1 == 1
