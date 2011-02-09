#!/usr/bin/env python
import os
import sys

from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASE_ENGINE='sqlite3',
        DATABASE_NAME=':memory:',
        INSTALLED_APPS=[
            'contextual',
            'contextual.tests',
        ]
    )

from django.test.simple import run_tests as django_run_tests

def run_tests():
    parent = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
    )
    sys.path.insert(0, parent)
    failures = django_run_tests(['tests'], verbosity=1, interactive=True)
    sys.exit(failures)

if __name__ == '__main__':
    run_tests()
