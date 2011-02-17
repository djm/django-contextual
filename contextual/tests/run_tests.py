#!/usr/bin/env python
import os
import sys

from django import VERSION as DJANGO_VERSION
from django.conf import settings

VERBOSITY = 1
TEST_LABELS = ["tests"]

if not settings.configured:
    settings.configure(
        DATABASE_ENGINE='sqlite3',
        DATABASE_NAME=':memory:',
        INSTALLED_APPS=[
            'contextual',
            'contextual.tests',
        ]
    )


def run_tests():
    parent = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
    )
    sys.path.insert(0, parent)
    if DJANGO_VERSION < (1, 2):
        from django.test.simple import run_tests
        failures = run_tests(TEST_LABELS, verbosity=VERBOSITY, interactive=True)
    else:
        from django.test.simple import DjangoTestSuiteRunner
        runner = DjangoTestSuiteRunner(verbosity=VERBOSITY, interactive=True)
        failures = runner.run_tests(TEST_LABELS)
    sys.exit(failures)

if __name__ == '__main__':
    run_tests()
