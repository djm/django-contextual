#django-contextual

contextual (*adj*); Specific to the conditions in which something exists or occurs.

Put simply, this app allows the replacement of tags in HTML output with data
which is chosen based upon tests passed on the request. A couple of examples:

* You may want the phone number displayed on your site to change based upon
  whether the incoming user came from natural or search traffic so you can
  better tailor your offline tracking.

* You may want to display a different contact email address for users coming
  from a specific referrer.

* You way want to swap your stylesheets out based upon whether someone provides
  a query string to the page.

This app handles those use cases and *tries* to stay customisable in that you
can you can hook in your own request tests and provide any custom
models/configuration settings that are required for that test.

##Requirements

Tests pass on Django 1.1 and 1.2; I haven't got around to testing it on more releases
yet. If you find an issue, please report it.

Currently this app requires the use of `django.contrib.sessions`; so that must
be installed and in use on your project. More ways to allow "persistence" are in
the pipeline.

## Why does it act on the response rather than during template rendering?

Because we needed the replacements to occur not only in raw HTML templates but also
from data input into our various CMSs and therefore stored in the DB with the relevant
tags - to rely on tags & filters would have meant a lot of repetition due to filters
on all the database variables being output; I believe this way goes along with DRY, 
feel free to disagree though.

##Install and (Basic) Usage

1. Make sure the app is in your python path. Either download and run `python setup.py install` or install with `pip install -e https://github.com/djm/django-contextual.git`.
2. Add the app to your project's `INSTALLED_APPS` setting as `contextual`.
3. Add the app's middleware to your project's `MIDDLEWARE_CLASSES` as `contextual.middleware.ContextualMiddleware`. Order is important, the response part needs to work on plain text so must become before any gzip compression etc and therefore AFTER any middleware which does something like that in the setting list. See [the django docs](http://docs.djangoproject.com/en/dev/topics/http/middleware/) for ordering help.
3. Set up the `CONTEXTUAL_TESTS` setting. More on this below, you can see the defaults in `contextual/defaults.py`.
4. Run `python manage.py syncdb` to install the required models (based on the tests you chose).
5. Set up your replacement tags e.g `PHONE`, `EMAIL` in the admin and add your required replacement data (name wisely).
6. Create your tests in the admin (more on the default ones below) and attach the replacements they should carry out.
7. Replacements should now work in your templates and DB. (Using the examples earlier as [PHONE] and [EMAIL].)

**The tag choices are cached so you may need to clear your cache to get any new tag additions.**
 #TODO: Add cache invalidation on new tags.

##Using the In-built Contextual Tests

Docs coming shortly.

##Writing your own Contextual Tests

Docs coming soon.. see `contextual/contextual_tests.py`. They are fairly simple.

##Contributing (Forking)

All contributions are thoroughly welcome; the contextual (request) tests included 
are standard ones that we have required again and again but there's plenty more 
room in this package for more should you wish to fork and send a pull request.

## License

This is BETA software released under the standard BSD License.
