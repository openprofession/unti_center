from django import template

register = template.Library()


@register.filter
def as_percentage_of(value, whole):
    try:
        return "%d%%" % (value / whole * 100)
    except (ValueError, ZeroDivisionError):
        return ""


@register.filter
def as_percentage_of_round5(value, whole):
    try:
        return round((value / whole * 100 + 3) / 5) * 5
    except (ValueError, ZeroDivisionError):
        return 0
