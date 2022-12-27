# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.filter
def field_widget_type(field):
    """Get input type of field."""
    return field.field.widget.input_type
