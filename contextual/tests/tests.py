from django.core.exceptions import ImproperlyConfigured
from django.core.handlers.wsgi import WSGIRequest
from django.test import TestCase
from django.test import Client

from contextual.contextual_models import (HostnameTestModel, PathTestModel, 
        QueryStringTestModel, RefererTestModel, BrandedSearchRefererTestModel)
from contextual.contextual_tests import (HostnameTest, PathTest, QueryStringTest, 
        RefererTest, BrandedSearchRefererTest)
from contextual.defaults import DEFAULT_SEARCH_ENGINES
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

    def request(self, **request):
        """
        Similar to parent class, but returns the request object as 
        soon as it has created it.
        """
        environ = {}
        environ.update(self.defaults)
        environ.update(default_environ)
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
        request = self.req_factory.request(HTTP_HOST="www.cantfindme.com")
        match = self.test.test(request)
        assert match is None

    def test_localhost_lookup(self):
        """
        Test the match returns for our port based hostname.
        """
        request = self.req_factory.request(HTTP_HOST="127.0.0.1:8000")
        match = self.test.test(request)
        assert match == self.hostname_test3

class PathRequestTest(BaseTestCase):

    def setUp(self):
        """
        Create a couple of path based tests.
        """
        super(PathRequestTest, self).setUp()
        self.path_test1 = PathTestModel.objects.create(path='/')
        self.path_test2 = PathTestModel.objects.create(path='/parent/')
        self.path_test3 = PathTestModel.objects.create(path='/parent/child/')
        self.test = PathTest()

    def test_match_root(self):
        request = self.req_factory.request()
        match = self.test.test(request)
        assert match == self.path_test1

    def test_match_exact_path(self):
        request = self.req_factory.request(PATH_INFO='/parent/')
        match = self.test.test(request)
        assert match == self.path_test2

    def test_match_doesnt_hit_child(self):
        request = self.req_factory.request(PATH_INFO='/parent/child')
        match = self.test.test(request)
        assert match is None

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
        query = "s=google-phone&something=234"
        request = self.req_factory.request(QUERY_STRING=query)
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
        query = "s=google-phone2"
        request = self.req_factory.request(QUERY_STRING=query)
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
        query = "correct=google-phone"
        request = self.req_factory.request(QUERY_STRING=query)
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

class RefererRequestTest(BaseTestCase):

    def setUp(self):
        """
        Create some referer tests.
        """
        super(RefererRequestTest, self).setUp()
        self.referer_test1 = RefererTestModel.objects.create(domain="www.google.com")
        self.referer_test2 = RefererTestModel.objects.create(domain="google.com")
        self.test = RefererTest()

    def test_simple_lookup(self):
        referer_url = "http://www.google.com/search?sclient=psy&hl=en&site=&source=hp&q=test&aq=f&aqi=&aql=&oq=&pbx=1&cad=cbv"
        request = self.req_factory.request(HTTP_REFERER=referer_url)
        match = self.test.test(request)
        assert match == self.referer_test1

    def test_lookup_fail(self):
        referer_url = "http://www.google.fr/search?sclient=psy&hl=en&site=&source=hp&q=test&aq=f&aqi=&aql=&oq=&pbx=1&cad=cbv"
        request = self.req_factory.request(HTTP_REFERER=referer_url)
        match = self.test.test(request)
        assert match is None

    def test_non_subdomain_match(self):
        referer_url = "http://google.com/search?sclient=psy&hl=en&site=&source=hp&q=test&aq=f&aqi=&aql=&oq=&pbx=1&cad=cbv"
        request = self.req_factory.request(HTTP_REFERER=referer_url)
        match = self.test.test(request)
        assert match == self.referer_test2

class BrandedSearchRefererRequestTest(BaseTestCase):
    """
    This test is designed to work with the DEFAULT_SEARCH_ENGINES
    """

    def setUp(self):
        """
        Create a couple of branded search referer tests.
        """
        super(BrandedSearchRefererRequestTest, self).setUp()
        for key in DEFAULT_SEARCH_ENGINES.iterkeys():
            BrandedSearchRefererTestModel.objects.create(search_engine=key, branded=False)
            BrandedSearchRefererTestModel.objects.create(search_engine=key, branded=True)
        self.brand_terms = ["brand", "branded", "branded.co.uk"]
        config = {'brand_terms': self.brand_terms}
        self.test = BrandedSearchRefererTest(config)

    def test_no_then_incorrect_then_correct_config_dict(self):
        try:
            test = BrandedSearchRefererTest()
        except ImproperlyConfigured:
            pass
        else:
            assert False, "No config dictionary supplied and yet no error!"
        config = {'brands': ["branded"]}
        try:
            test = BrandedSearchRefererTest(config)
        except ImproperlyConfigured:
            pass
        else:
            assert False, "Incorrect key in config dictionary and yet no error!"
        config = {'brand_terms': ["branded"]}
        try:
            test = BrandedSearchRefererTest(config)
        except ImproperlyConfigured:
            assert False, "Correct key in config dictionary but we're getting an error."

    def test_no_referer(self):
        """
        Test that no referer returns No match and doesn't 500.
        """
        request = self.req_factory.request(HTTP_REFERER="")
        match = self.test.test(request)
        assert match is None

    def test_partial_referer(self):
        """
        Test that a partial referer returns no match and doesn't 500.
        """
        request = self.req_factory.request(HTTP_REFERER="http://")
        match = self.test.test(request)
        assert match is None

    def test_no_query_string_on_referer(self):
        referer_url = "http://www.google.co.uk/"
        request = self.req_factory.request(HTTP_REFERER=referer_url)
        match = self.test.test(request)
        assert match.search_engine == 'google'
        # With no query string, we should always be unbranded.
        assert match.branded == False

    """
    Branded counts as search terms which include the branded terms we set in setUp.
    Unbranded is any other search term which does not contain those terms.
    """

    def test_ask_branded(self):
        # Branded as it has the word "branded" in the query..
        referer_url = "http://uk.ask.com/web?q=branded+test&search=&qsrc=0&o=312&l=dir"
        request = self.req_factory.request(HTTP_REFERER=referer_url)
        match = self.test.test(request)
        assert match.search_engine == 'ask'
        assert match.branded == True

    def test_ask_unbranded(self):
        referer_url = "http://uk.ask.com/web?q=random+test&search=&qsrc=0&o=312&l=dir"
        request = self.req_factory.request(HTTP_REFERER=referer_url)
        match = self.test.test(request)
        assert match.search_engine == 'ask'
        assert match.branded == False

    def test_bing_branded(self):
        referer_url = "http://www.bing.com/search?q=branded.co.uk+test+term&go=&form=QBRE&filt=all&qs=n&sk="
        request = self.req_factory.request(HTTP_REFERER=referer_url)
        match = self.test.test(request)
        assert match.search_engine == 'bing'
        assert match.branded == True

    def test_bing_unbranded(self):
        referer_url = "http://www.bing.com/search?q=random+test+term&go=&form=QBRE&filt=all&qs=n&sk="
        request = self.req_factory.request(HTTP_REFERER=referer_url)
        match = self.test.test(request)
        assert match.search_engine == 'bing'
        assert match.branded == False

    def test_google_instant_branded(self):
        referer_url = "http://www.google.com/#sclient=psy&hl=en&q=branded.co.uk+test+term&aq=f&aqi=&aql=&oq=&pbx=1&fp=31bd50ee20ddd9f2"
        request = self.req_factory.request(HTTP_REFERER=referer_url)
        match = self.test.test(request)
        assert match.search_engine == 'google'
        assert match.branded == True

    def test_google_instant_unbranded(self):
        referer_url = "http://www.google.com/#sclient=psy&hl=en&q=term+search+random&aq=f&aqi=&aql=&oq=&pbx=1&fp=31bd50ee20ddd9f2"
        request = self.req_factory.request(HTTP_REFERER=referer_url)
        match = self.test.test(request)
        assert match.search_engine == 'google'
        assert match.branded == False

    def test_google_normal_branded(self):

        referer_url = "http://www.google.com/search?hl=en&source=hp&biw=1680&bih=860&q=search+test+branded&aq=f&aqi=&aql=&oq="
        request = self.req_factory.request(HTTP_REFERER=referer_url)
        match = self.test.test(request)
        assert match.search_engine == 'google'
        assert match.branded == True

    def test_google_normal_unbranded(self):
        referer_url = "http://www.google.com/search?hl=en&biw=1680&bih=860&q=search+test+random&aq=f&aqi=&aql=&oq="
        request = self.req_factory.request(HTTP_REFERER=referer_url)
        match = self.test.test(request)
        assert match.search_engine == 'google'
        assert match.branded == False

        assert match.branded == False

    def test_yahoo_branded(self):
        referer_url = "http://uk.search.yahoo.com/search;_ylt=Anai_uHQTTS4fYw9WKSHXNk4hJp4?vc=&p=brand+search+term&toggle=1&cop=mss&ei=UTF-8&fr=yfp-t-702"
        request = self.req_factory.request(HTTP_REFERER=referer_url)
        match = self.test.test(request)
        assert match.search_engine == 'yahoo'
        assert match.branded == True

    def test_yahoo_unbranded(self):
        referer_url = "http://uk.search.yahoo.com/search;_ylt=Anai_uHQTTS4fYw9WKSHXNk4hJp4?vc=&p=random+search+term&toggle=1&cop=mss&ei=UTF-8&fr=yfp-t-702"
        request = self.req_factory.request(HTTP_REFERER=referer_url)
        match = self.test.test(request)
        assert match.search_engine == 'yahoo'
        assert match.branded == False
