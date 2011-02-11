from django.db import models

class ActiveManager(models.Manager):
    """
    Simple manager which overrides the queryset
    retrieval method to only return those models
    who have their active attribute set to True.
    """

    def get_query_set(self):
        return super(ActiveManager, self).get_query_set().filter(active=True)
