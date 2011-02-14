"""
This file is for providing default settings, these can and should
be overridden with your Django project's settings.py.
"""
from django.conf import settings

# Tuple triplets defining modules to load, their matching priority 
# and an optional config dictionary to pass to the test.
DEFAULT_TESTS = (
        ('contextual.contextual_tests.RefererTest', 1),
        ('contextual.contextual_tests.QueryStringTest', 2, {'get_key': 's'}),
       #('contextual.contextual_tests.HostnameTest', 3),
)

DEFAULT_SESSION_KEY = "contextual_test"

TESTS = getattr(settings, 'CONTEXTUAL_TESTS', DEFAULT_TESTS)
SESSION_KEY = getattr(settings, 'CONTEXTUAL_SESSION_KEY', DEFAULT_SESSION_KEY)
