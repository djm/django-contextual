from django.core.exceptions import ImproperlyConfigured
from django.core.handlers.wsgi import WSGIRequest
from django.test import TestCase
from django.test import Client

from contextual.contextual_models import (HostnameTestModel, QueryStringTestModel,
                                        RefererTestModel)
from contextual.contextual_tests import HostnameTest, QueryStringTest, RefererTest
from contextual.models import ReplacementData, ReplacementTag

default_environ = {
    'HTTP_HOST': 'www.example.com',
    'PATH_INFO': '/',
    'QUERY_STRING': '',
    'REQUEST_METHOD': 'GET',
    'SERVER_NAME': 'testserver',
    'SERVER_PORT': 80,
    'SERVER_PROTOCOL': 'HTTP/1.1',
}

class RequestFactory(Client):
    """
    Class that lets you create mock Request objects for use in testing.
    
    Adapted from simonw's http://djangosnippets.org/snippets/963/
    """

    def request(self, environ=default_environ, **request):
        """
        Similar to parent class, but returns the request object as 
        soon as it has created it.
        """
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
        # Set up request factory.
        self.req_factory = RequestFactory()
        

class GeneralTests(BaseTestCase):

    def test_active_manager_and_data_tag_link(self):
        # We've set up 3 ReplacementData objects which default to being active.
        assert ReplacementData.objects.all().count() == 3
        # Make one inactive and re-test.
        self.data_another.active = False
        self.data_another.save()
        assert ReplacementData.objects.all().count() == 2
        # Reactive and test again.
        self.data_another.active = True
        self.data_another.save()
        assert ReplacementData.objects.all().count() == 3
        # Assert that the replacement data is indeed attached to the tag.
        assert self.tag_phone.replacement_data.all().count() == 3


class HostnameRequestTest(BaseTestCase):

    def setUp(self):
        """
        Create a couple of hostname tests.
        """
        super(HostnameRequestTest, self).setUp()
        self.hostname_test1 = HostnameTestModel.objects.create(hostname="www.example.com")
        self.hostname_test2 = HostnameTestModel.objects.create(hostname="example.com")
        self.hostname_test3 = HostnameTestModel.objects.create(hostname="127.0.0.1:8000")
        # And link to replacement data.
        self.hostname_test1.replacements.add(self.data_host)
        self.hostname_test2.replacements.add(self.data_host)
        self.hostname_test3.replacements.add(self.data_another)
        # Set up middleware test.
        self.test = HostnameTest()


    def test_creation(self):
        assert HostnameTestModel.objects.all().count() == 3
        assert HostnameTestModel.objects.filter(hostname__icontains="example").count() == 2

    def test_simple_lookup(self):
        """
        With the default request environ this should return
        a match with our www.example.com hostnametest
        """
        request = self.req_factory.request()
        match = self.test.test(request)
        assert match == self.hostname_test1

    def test_deliberate_fail(self):
        """
        Create a request with a HTTP_HOST we shouldn't
        have a match for, test we return None.
        """
        environ = {}
        environ.update(default_environ)
        environ['HTTP_HOST'] = "www.cantfindme.com"
        request = self.req_factory.request(environ)
        match = self.test.test(request)
        assert match is None

    def test_localhost_lookup(self):
        """
        Test the match returns for our port based hostname.
        """
        environ = {}
        environ.update(default_environ)
        environ['HTTP_HOST'] = "127.0.0.1:8000"
        request = self.req_factory.request(environ)
        match = self.test.test(request)
        assert match == self.hostname_test3


class QueryStringRequestTest(BaseTestCase):

    def setUp(self):
        """
        Create a couple of query string tests.
        """
        super(QueryStringRequestTest, self).setUp()
        self.querystring_test1 = QueryStringTestModel.objects.create(value="google-phone")
        self.querystring_test2 = QueryStringTestModel.objects.create(value="space test")
        # And link to replacement data.
        self.querystring_test1.replacements.add(self.data_host)
        self.querystring_test2.replacements.add(self.data_host)

    def test_simple_lookup(self):
        """
        Given a query string containing the key s; which
        is the one we're meant to check (specified in the config
        dictionary), this will return the appropriate test match.
        """
        environ = {}
        environ.update(default_environ)
        environ['QUERY_STRING'] = "s=google-phone&something=234"
        request = self.req_factory.request(environ)
        config = {'get_key': 's'}
        test = QueryStringTest(config)
        match = test.test(request)
        assert match == self.querystring_test1

    def test_deliberate_config_fail(self):
        """
        The QueryStringTest class requires a 'get_key'
        key in its instantiation config dictionary.
        Here we don't give it and hope it fails.
        """
        config = {'pointless': 'incorrect'}
        try:
            test = QueryStringTest(config)
        except ImproperlyConfigured:
            pass
        else:
            assert False, "Should fail in loading this config dictionary."

    def test_deliberate_lookup_fail(self):
        """
        Fail on slug lookup.
        """
        environ = {}
        environ.update(default_environ)
        environ['QUERY_STRING'] = "s=google-phone2"
        request = self.req_factory.request(environ)
        # Correct config, we're testing failed
        # slug lookup not the key here.
        config = {'get_key': 's'}
        test = QueryStringTest(config)
        match = test.test(request)
        assert match is None

    def test_deliberate_fail_due_to_wrong_key(self):
        """
        Correct slug value lookup but on the wrong key,
        we'll change the config dict here and try again
        to make sure it passes with the correct get_key
        value.
        """
        environ = {}
        environ.update(default_environ)
        environ['QUERY_STRING'] = "correct=google-phone"
        request = self.req_factory.request(environ)
        # Deliberately non-matching config dict
        config = {'get_key': 'incorrect'}
        test = QueryStringTest(config)
        match = test.test(request)
        assert match is None
        # Fix the config dict and try again with same query string.
        config['get_key'] = 'correct'
        test = QueryStringTest(config)
        match = test.test(request)
        assert match == self.querystring_test1
