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
    replacements = models.ManyToManyField('contextual.Replacement',
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
                help_text="Set to value of HTTP_HOST for positive match.")


class QueryStringTestModel(BaseTestModel):
    """
    Allows for rule matching based on query string.
    """
    pass

class RefererTestModel(BaseTestModel):
    """
    Allows for rule matching based on the HTTP_REFERER header.
    """
    # Yes referrer is spelt wrong, to keep in line
    # with the incorrect spelling of the HTTP header.
    pass
