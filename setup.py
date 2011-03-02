import os
import sys
from setuptools import setup, find_packages

os.environ['DJANGO_SETTINGS_MODULE'] = 'contextual.tests.settings'

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
readme = f.read()
f.close()

setup(
    name='django-contextual',
    version='0.1',
    description='A django app that provides pluggable contextual replacement '
                'functionality. e.g Changing a phone number based upon the '
                'query string, hostname, referrer etc.',
    long_description=readme,
    author='Darian Moody',
    author_email='mail@djm.org.uk',
    url='https://github.com/djm/django-contextual',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        ],
    test_suite='contextual.tests.run_tests.run_tests',
)
