from urllib.parse import urlencode
from django import template
from babel.numbers import format_currency

from ledger.backend import getUserGroup

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    query.pop('page', None)
    query.pop('sucessful', None)
    query.pop('lr-no', None)
    query.pop('update', None)
    query.pop('invalid', None)
    query.update(kwargs)
    return query.urlencode()

@register.simple_tag(takes_context=True)
def get_shop(context, **kwargs):
    user = context['request'].user
    user_group = getUserGroup(user)
    if user_group:
        return user_group.shop
    return context['request'].user.username

@register.filter
def format_numeric(value):
    if value!=None and type(value)==float:
        return format_currency(value, 'INR', locale='en_IN')
    return value

@register.filter
def format_numeric_if_possible(value):
    if value!=None and int(value)==value:
        return int(value)
    return value