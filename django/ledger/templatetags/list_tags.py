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
    query.pop('l_r_view', None)
    query.pop('approve', None)
    query.update(kwargs)
    return query.urlencode()

@register.simple_tag(takes_context=True)
def get_shop(context, **kwargs):
    user = context['request'].user
    user_group = getUserGroup(user)
    if user_group and getattr(user_group, 'shop', None):
        return user_group.shop
    return "Cash Center"

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

@register.filter
def get_column_icon(key):
    """Return appropriate Font Awesome icon for ledger column name."""
    icon_map = {
        'l_r_no': 'fa-hashtag',
        'l_r_date': 'fa-calendar',
        'no_of_bale': 'fa-cube',
        'bale_no': 'fa-cube',
        'item': 'fa-tag',
        'transport': 'fa-truck',
        'status': 'fa-check-circle',
        'supplier': 'fa-building',
        'location': 'fa-map-marker',
        'pcs_mtr': 'fa-ruler',
        'price': 'fa-money',
        'weight': 'fa-balance-scale',
        'frieght': 'fa-shipping-fast',
        'delivery': 'fa-calendar-check-o',
        'reciept': 'fa-file-text',
        'hsn_code': 'fa-barcode',
        'bill_ammount': 'fa-money-bill',
        'remark': 'fa-comment',
    }
    return icon_map.get(key, 'fa-sort')


@register.filter
def underscore_to_space(value):
    """Replace underscores in a string with spaces."""
    if value is None:
        return ''
    return str(value).replace('_', ' ')
