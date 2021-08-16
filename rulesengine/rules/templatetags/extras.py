
from django import template

register = template.Library()

register.simple_tag(lambda a, b: a == b, name='is_eq')
