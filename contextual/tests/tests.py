from django.core.handlers.wsgi import WSGIRequest
from django.test import TestCase
from django.test import Client

from contextual.contextual_models import HostnameTestModel
from contextual.contextual_tests import HostnameTest
from contextual.models import ReplacementData, ReplacementTag

default_environ = {
    'HTTP_HOST': 'www.example.com',
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
    
    Adapted from simonw's http://djangosnippets.org/snippets/963/
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
        environ = self.environ.copy()
        environ.update(self.defaults)
        environ.update(request)
        return WSGIRequest(environ)


class BaseTestCase(TestCase):

    def setUp(self):
        """
        Create a bunch of replacement data and tags for the tests.
        """
        self.tag_phone = ReplacementTag.objects.create(tag="PHONE", 
                                                       default="0800 DEFAULT")
        self.data_host = ReplacementData.objects.create(tag=self.tag_phone, 
                                                        name="Host", 
                                                        data="0800 HOST")
        self.data_google = ReplacementData.objects.create(tag=self.tag_phone, 
                                                          name="Google",
                                                          data="0800 GOOGLE")
        self.data_another = ReplacementData.objects.create(tag=self.tag_phone, 
                                                           name="Another",
                                                           data="0800 ANOTHER")


class HostnameRequestTest(BaseTestCase):

    def setUp(self):
        """
        Create a couple of hostname tests.
        """
        super(HostnameRequestTest, self).__init__()
        hostname_test1 = HostnameTestModel.objects.create(hostname="www.example.com")
        hostname_test2 = HostnameTestModel.objects.create(hostname="example.com")
        hostname_test3 = HostnameTestModel.objects.create(hostname="127.0.0.1:8000")
        # And link to replacement data.
        hostname_test1.replacements.add(self.data_host)
        hostname_test2.replacements.add(self.data_host)
        hostname_test3.replacements.add(self.data_another)


    def test_a_test(self):
        import ipdb; ipdb.set_trace();
        assert 1 == 1
