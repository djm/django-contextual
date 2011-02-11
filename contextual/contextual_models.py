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


class QueryStringTestModel(BaseTestModel):
    """
    Allows for rule matching based on query string.
    """
    value = models.CharField(_("value"), max_length=255,
             help_text="Set to exact value. Key to check in defined in config." )

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

    class Meta:
        verbose_name = "referer based test"

    def __unicode__(self):
        return u"Referer Test: "
