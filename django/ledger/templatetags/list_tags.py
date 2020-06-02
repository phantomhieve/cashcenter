from urllib.parse import urlencode
from django import template

from ledger.backend import getUserGroup

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    query.update(kwargs)
    return query.urlencode()

@register.simple_tag(takes_context=True)
def get_shop(context, **kwargs):
    user = context['request'].user
    user_group = getUserGroup(user)
    if user_group:
        return user_group.shop
    return context['request'].user.username
