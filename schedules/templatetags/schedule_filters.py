from django import template

register = template.Library()

@register.filter
def status_color(status):
    """Return appropriate color class for schedule status"""
    color_map = {
        'pending': 'yellow',
        'approved': 'green', 
        'rejected': 'red',
        'completed': 'blue',
        'cancelled': 'gray',
    }
    return color_map.get(status.lower(), 'gray')
