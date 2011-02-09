# This file is for providing default settings, these can and should
# be overridden with your Django project's settings.py.

# This is a list of raw stings that replacement may occur on.
CONTEXTUAL_REPLACEMENT_TAGS = [r'[PHONE]', r'[ADDRESS]']

# Tuple triplets defining modules to load, their matching priority 
# and an optional config dictionary to pass to the test.
CONTEXTUAL_TESTS = (
        ('contextual.contextual_tests.HostnameTest', 1),
       # ('contextual.contextual_tests.QueryStringTest', 2, {}),
       # ('contextual.contextual_tests.RefererTest', 3, {}),
)
