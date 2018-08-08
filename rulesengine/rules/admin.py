from django.contrib import admin

from .models import (
    Rule,
    RuleChange
)

# Register your models here.
admin.site.register(Rule)
admin.site.register(RuleChange)
