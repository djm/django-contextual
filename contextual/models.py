from django.db import models
from django.utils.translation import ugettext_lazy as _

from contextual.managers import ActiveManager


class ReplacementData(models.Model):
    """
    A piece of data which will get inserted in place
    of a tag in all html responses that match the rules.
    """
    tag = models.ForeignKey('contextual.ReplacementTag', 
                            related_name="replacement_data")
    name = models.CharField(_("name"), max_length=100, 
                            help_text="Admin display purposes only.")
    data = models.CharField(_("replacement data"), max_length=100)
    active = models.BooleanField(_("active?"), default=True)

    all_objects = models.Manager()
    objects = ActiveManager()

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "replacement data"

    def __unicode__(self):
        return "%s: %s" % (self.tag, self.name)


class ReplacementTag(models.Model):
    """
    These model the replacement tags which are available
    to the project; we do this here rather than in the 
    settings so we can provide defaults for the replacement
    tags in a sensible fashion.
    """
    tag = models.CharField(_("replacement tag"), max_length=20,
                  help_text=_("e.g PHONE will be made available as [PHONE]"))
    default = models.CharField(_("default replacement"), max_length=255)

    class Meta:
        ordering = ["tag"]

    def __unicode__(self):
        return u"[%s]" % self.tag

    @property
    def raw_tag(self):
        return r"\[%s\]" % self.tag
