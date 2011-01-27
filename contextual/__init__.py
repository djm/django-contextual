from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from contextual.defaults import CONTEXTUAL_TESTS

TESTS = getattr(settings, 'CONTEXTUAL_TESTS', CONTEXTUAL_TESTS)

def test_setting_to_instance(test_setting):
    """
    Given a tuple triplet test setting, converts
    to an instance with optional config.
    """
    try:
        import_bits = test_setting[0].rsplit('.', 1)
        module = __import__(import_bits[0], fromlist=[import_bits[1]])
        klass = getattr(module, import_bits[1])
    except ImportError, e:
        raise ImproperlyConfigured("%s: check your CONTEXTUAL_TESTS setting." % e)
    if len(test_setting) < 3:
        instance = klass()
    else:
        instance = klass(**test_setting[2]) 
    return instance

def load_tests(tests):
    """
    Instantiates the tests we need to use, passing them
    an optional config dictionary and returns the test 
    instances in the order that they need to be processed,
    as it is a case of first match wins.

    Arguments: tests - An iterative of tuple triplets.
        e.g ('test.module.path', priority_as_int, config_dict)
    """
    test_instances = []
    # We can't trust the iterative to be in the correct
    # priority order already, so first we sort.
    tests = sorted(tests, key=lambda x: x[1])
    for test in tests:
        # A quick test to check setting was in 
        # correct format, helps the user.
        instance = test_setting_to_instance(test)
        test_instances.append(instance)
    return test_instances

LOADED_TESTS = load_tests(TESTS)
