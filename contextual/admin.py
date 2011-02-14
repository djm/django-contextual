from django.contrib import admin

from contextual.models import ReplacementData, ReplacementTag

class ReplacementDataAdminInline(admin.TabularInline):
    model = ReplacementData
    extra = 3

class ReplacementTagAdmin(admin.ModelAdmin):
    inlines = [ReplacementDataAdminInline]
    list_display = ['tag', 'default']
    search_fields = ['tag', 'default']

admin.site.register(ReplacementTag, ReplacementTagAdmin)
