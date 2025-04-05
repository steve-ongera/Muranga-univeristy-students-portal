# In your templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def split(value, arg):
    return value.split(arg)[0]

# In your_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_programme_name(group_string):
    return group_string.split(' (')[0]