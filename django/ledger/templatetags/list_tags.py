from urllib.parse import urlencode
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    query.update(kwargs)
    return query.urlencode()

@register.simple_tag(takes_context=True)
def get_shop(context, **kwargs):
    user = context['request'].user
    primary =  user.primary_user.filter().values('shop')
    main    =  user.main_user.filter().values('shop')
    if primary: return primary[0]['shop']
    elif main: return f"{main[0]['shop']} - Admin"
    return 'Super User'
