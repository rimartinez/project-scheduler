from django import template
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag
def button(text, variant="primary", size="default", icon=None, **kwargs):
    """Render a shadcn/ui button component"""
    context = {
        'text': text,
        'variant': variant,
        'size': size,
        'icon': icon,
        'class': kwargs.get('class', ''),
        'type': kwargs.get('type', 'button'),
        'onclick': kwargs.get('onclick', ''),
        'disabled': kwargs.get('disabled', False),
    }
    return render_to_string('components/button.html', context)

@register.simple_tag
def card(title=None, description=None, content=None, footer=None, **kwargs):
    """Render a shadcn/ui card component"""
    context = {
        'title': title,
        'description': description,
        'content': content,
        'footer': footer,
        'class': kwargs.get('class', ''),
    }
    return render_to_string('components/card.html', context)

@register.simple_tag
def input_field(name, label=None, placeholder=None, type="text", required=False, **kwargs):
    """Render a shadcn/ui input field"""
    context = {
        'name': name,
        'label': label,
        'placeholder': placeholder,
        'type': type,
        'required': required,
        'value': kwargs.get('value', ''),
        'class': kwargs.get('class', ''),
        'error': kwargs.get('error', ''),
    }
    return render_to_string('components/input.html', context)

@register.simple_tag
def badge(text, variant="default", **kwargs):
    """Render a shadcn/ui badge component"""
    context = {
        'text': text,
        'variant': variant,
        'class': kwargs.get('class', ''),
    }
    return render_to_string('components/badge.html', context)

@register.simple_tag
def table(headers, rows, **kwargs):
    """Render a shadcn/ui table component"""
    context = {
        'headers': headers,
        'rows': rows,
        'class': kwargs.get('class', ''),
    }
    return render_to_string('components/table.html', context)

@register.simple_tag
def alert(title=None, description=None, variant="default", **kwargs):
    """Render a shadcn/ui alert component"""
    context = {
        'title': title,
        'description': description,
        'variant': variant,
        'class': kwargs.get('class', ''),
    }
    return render_to_string('components/alert.html', context)

@register.simple_tag
def calendar(month, year, events=None, **kwargs):
    """Render a shadcn/ui calendar component"""
    context = {
        'month': month,
        'year': year,
        'events': events or [],
        'class': kwargs.get('class', ''),
    }
    return render_to_string('components/calendar.html', context)

@register.simple_tag
def form_group(label, field, error=None, description=None, **kwargs):
    """Render a shadcn/ui form group"""
    context = {
        'label': label,
        'field': field,
        'error': error,
        'description': description,
        'class': kwargs.get('class', ''),
    }
    return render_to_string('components/form_group.html', context)

@register.simple_tag
def nav_link(text, url, active=False, icon=None, **kwargs):
    """Render a shadcn/ui navigation link"""
    context = {
        'text': text,
        'url': url,
        'active': active,
        'icon': icon,
        'class': kwargs.get('class', ''),
    }
    return render_to_string('components/nav_link.html', context)
