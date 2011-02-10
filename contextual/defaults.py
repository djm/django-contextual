"""
This file is for providing default settings, these can and should
be overridden with your Django project's settings.py.
"""
from django.conf import settings

# This is a list of raw stings that replacement may occur on.
DEFAULT_REPLACEMENT_TAGS = {
    'PHONE': "default-phone",
    'ADDRESS': "default-address",
}

# Tuple triplets defining modules to load, their matching priority 
# and an optional config dictionary to pass to the test.
DEFAULT_TESTS = (
        ('contextual.contextual_tests.QueryStringTest', 1, {'get_key': 's'}),
        ('contextual.contextual_tests.HostnameTest', 2),
       # ('contextual.contextual_tests.RefererTest', 3, {}),
)

REPLACEMENT_TAGS = getattr(settings, 'CONTEXTUAL_REPLACEMENT_TAGS', 
                           DEFAULT_REPLACEMENT_TAGS)
TESTS = getattr(settings, 'CONTEXTUAL_TESTS', DEFAULT_TESTS)
