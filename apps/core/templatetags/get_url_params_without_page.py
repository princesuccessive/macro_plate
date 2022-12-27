from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_url_params_without_page(context) -> str:
    """Return GET request query params without `page`, default to empty str."""
    url_params = context['request'].GET.copy()
    url_params.pop('page', None)
    if url_params:
        return '&' + url_params.urlencode()
    return ''
