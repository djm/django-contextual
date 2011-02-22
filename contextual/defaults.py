"""
This file is for providing default settings, these can and should
be overridden with your Django project's settings.py.
"""
from django.conf import settings

# Tuple triplets defining modules to load, their matching priority 
# and an optional config dictionary to pass to the test.
DEFAULT_TESTS = (
        ('contextual.contextual_tests.BrandedSearchRefererTest', 1, {'brand_terms': ["branded"]}),
        ('contextual.contextual_tests.RefererTest', 2),
        ('contextual.contextual_tests.QueryStringTest', 3, {'get_key': 's'}),
        ('contextual.contextual_tests.HostnameTest', 4),
)

# The name of the session key used to store the matching test over requests.
# Only provided as overrideble just in case of clashes.
DEFAULT_SESSION_KEY = "contextual_test"

# A dictionary of search engine domain names (without tld) as keys and 
# the GET key (field name) they use to store the search query as the value.
DEFAULT_SEARCH_ENGINES = {
    'ask': 'q',
    'bing': 'q',
    'google': 'q',
    'yahoo': 'p'
}

TESTS = getattr(settings, 'CONTEXTUAL_TESTS', DEFAULT_TESTS)
SESSION_KEY = getattr(settings, 'CONTEXTUAL_SESSION_KEY', DEFAULT_SESSION_KEY)
SEARCH_ENGINES = getattr(settings, 'CONTEXTUAL_SEARCH_ENGINES', DEFAULT_SEARCH_ENGINES)
