from django import template

register = template.Library()

AVATAR_COLORS = [
    '#3b5998', 
    '#dc3545', 
    '#28a745',  
    '#007bff',  
    '#6f42c1',  
    '#fd7e14', 
    '#20c997', 
    '#17a2b8', 
    '#6610f2',  
    '#e83e8c', 
]


@register.filter
def avatar_color(handle):
    if not handle:
        return '#3b5998'
    color_index = sum(ord(c) for c in handle.lower()) % len(AVATAR_COLORS)
    return AVATAR_COLORS[color_index]


@register.filter
def avatar_letter(handle):
    if not handle:
        return '?'
    return handle[0].upper()


@register.filter
def avatar_style(handle, size='120'):
    color = avatar_color(handle)
    letter = avatar_letter(handle)
    return f'background-color: {color}; color: white; width: {size}px; height: {size}px; border-radius: 3px; display: flex; align-items: center; justify-content: center; font-size: {int(size)//3}px; font-weight: bold; border: 4px solid white;'
