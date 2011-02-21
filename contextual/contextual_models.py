# This file is not called models.py as we don't
# want Django auto-loading all the available 
# models. Only the ones that are required as 
# described in the setting should be loaded.
# See defaults.py

from django.db import models
from django.utils.translation import ugettext_lazy as _

class BaseTestModel(models.Model):
    """
    The daddy test model, this provides the links
    and fields that should always be present.
    Subclass this if creating a new TestModel.
    """
    replacements = models.ManyToManyField('contextual.ReplacementData',
                       help_text="If this test is chosen as a match, these "
                              "replacements will be applied.",
                       verbose_name=_("replacements"),
                       related_name="%(class)s_replacements")

    class Meta:
        abstract = True
        app_label = 'contextual'


class HostnameTestModel(BaseTestModel):
    """
    Allows rule matching against specific hostnames.
    """
    hostname = models.CharField(_("hostname"), max_length=255, 
                help_text="Set to exact value of hostname for positive match.",
                unique=True)

    class Meta:
        verbose_name = "hostname test"

    def __unicode__(self):
        return u"Hostname Test: %s" % self.hostname

class PathTestModel(BaseTestModel):
    """
    Allows rule matching against specific URL paths (absolute).
    """
    path = models.CharField(_("request path"), max_length=255,
            help_text="Set to exact value of path for positive match.",
            unique=True)


class QueryStringTestModel(BaseTestModel):
    """
    Allows for rule matching based on query string.
    """
    value = models.CharField(_("value"), max_length=255,
             help_text="Set to exact value. Key to check in defined in config.",
             unique=True)

    class Meta:
        verbose_name = "querystring test"

    def __unicode__(self):
        return u"QueryString Test: %s" % self.value

class RefererTestModel(BaseTestModel):
    """
    Allows for rule matching based on the HTTP_REFERER header.
    """
    # Yes referrer is spelt wrong, to keep in line
    # with the incorrect spelling of the HTTP header.
    domain = models.CharField(_("referring domain"), max_length=255,
              help_text="Set to domain of referring site. e.g. 'google.com' or 'google.' to match all.",
              unique=True)

    class Meta:
        verbose_name = "referer based test"

    def __unicode__(self):
        return u"Referer Test: %s" % self.domain

class BrandedSearchRefererTestModel(BaseTestModel):
    """
    Allows for matching of requests from incoming search
    engines; splits up branded and unbranded search queries.
    """
    from contextual.defaults import SEARCH_ENGINES
    SEARCH_ENGINE_CHOICES = tuple(
                [(key, key.title()) for key in SEARCH_ENGINES.iterkeys()]
            )
    search_engine = models.CharField(_("search engine"), max_length=20,
            choices=SEARCH_ENGINE_CHOICES, help_text="The search engine to match for.")
    branded = models.BooleanField(_("branded?"),
            help_text="If branded, will only match when search term contained branded words.")

    class Meta:
        unique_together = ('search_engine', 'branded')
        verbose_name = "branded search referer test"

    def __unicode__(self):
        return u"Search referer: %s %s" % (
                self.search_engine.title(),
                "Branded" if self.branded else "Unbranded")
