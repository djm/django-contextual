from django.contrib import admin

from contextual.models import ReplacementData, ReplacementTag

class ReplacementDataAdmin(admin.ModelAdmin):
    list_display = ['name', 'data', 'tag', 'active']
    list_filter = ['active', 'tag']
    search_fields = ['name', 'data']

class ReplacementTagAdmin(admin.ModelAdmin):
    list_display = ['tag', 'default']
    search_fields = ['tag', 'default']

admin.site.register(ReplacementData, ReplacementDataAdmin)
admin.site.register(ReplacementTag, ReplacementTagAdmin)
