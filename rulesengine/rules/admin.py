from django.contrib import admin

from .models import (
    Rule,
    RuleChange
)

# Register your models here.
class RuleAdmin(admin.ModelAdmin):
    list_display = ("policy", "surt", "collection", "partner", "capture_date_start", "capture_date_end", "enabled")
    list_filter = ("enabled", "partner", "collection")
    search_fields = ("surt",)
admin.site.register(Rule, RuleAdmin)
admin.site.register(RuleChange)
