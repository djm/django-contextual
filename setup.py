import os
from setuptools import setup, find_packages

f = open(os.path.join(os.path.dirname(__file__), 'README'))
readme = f.read()
f.close()

setup(
        name='django-contextual',
        version='0.1',
        description='A django app that provides pluggable contextual replacement '
                    'functionality. e.g Changing a phone number based upon the '
                    ' query string, hostname, referrer etc.',
        long_description=readme,
        author='Darian Moodyu',
        author_email='mail@djm.org.uk',
        url='https://github.com/djm/django-contextual',
        packages=find_packages(),
        include_package_data=True,
        install_requires=[],
        classifiers=[
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Framework :: Django',
            ],
        )
