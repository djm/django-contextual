from django.db import models
from django.utils.translation import ugettext_lazy as _

class Replacement(models.Model):
    """
    A piece of data which will get inserted in place
    of a tag in all html responses that match the rules.
    """
    name = models.CharField(_("name"), max_length=100, 
                            help_text="Admin display purposes only.")
    data = models.CharField(_("replacement data"), max_length=100)
    tag = models.CharField(_("replacement tag"), max_length=20,
                           help_text=_("e.g. [PHONE]"))
