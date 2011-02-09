from django.contrib import admin

from contextual.models import Replacement

class ReplacementAdmin(admin.ModelAdmin):
    list_display = ['name', 'data', 'tag']
    search_fields = ['name', 'data', 'tag']

admin.site.register(Replacement, ReplacementAdmin)
