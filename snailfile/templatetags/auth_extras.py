from django import template
from django.contrib.auth.models import Group 

register = template.Library()

@register.filter(name='is_org')
def is_org(user): 
    return user.groups.filter(name__startswith='org_').exists()